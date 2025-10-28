const API_URL = "http://127.0.0.1:8000/tasks/";

let queryState = { search: "", completed: "" };

function buildQuery() {
    const params = new URLSearchParams();
    if (queryState.search) params.set("search", queryState.search);
    if (queryState.completed !== "") params.set("completed", queryState.completed);
    return params.toString();
}

async function fetchTasks() {
    const response = await fetch(API_URL + "?" + buildQuery());
    const tasks = await response.json();

    const list = document.getElementById("task-list");
    list.innerHTML = "";

    tasks.forEach(task => {
        const li = document.createElement("li");
        li.className = "task" + (task.completed ? " completed" : "");
        li.style.opacity = "0";
        li.style.transform = "translateY(6px)";
        const dueLine = task.due_time ? `<div class="task-due">Срок: ${new Date(task.due_time).toLocaleString()}</div>` : "";
        li.innerHTML = `
            <div class="task-header">
                <div class="task-title" onclick="toggleDescription(this)">
                    <span class="toggle-arrow">▼</span> ${task.title}
                </div>
                <div class="task-buttons">
                    <button class="complete" onclick="toggleComplete(${task.id}, ${!task.completed})">
                        ${task.completed ? "↩️" : "✅"}
                    </button>
                    <button onclick="deleteTask(${task.id})">🗑️</button>
                </div>
            </div>
            <div class="task-description">
                ${task.description ? task.description.replace(/\n/g, "<br>") : "<i>Нет описания</i>"}
                ${dueLine}
            </div>
        `;
        list.appendChild(li);
        requestAnimationFrame(() => {
            li.style.transition = "opacity .25s ease, transform .25s ease";
            li.style.opacity = "1";
            li.style.transform = "translateY(0)";
        });
    });
}

function toggleDescription(el) {
    const description = el.parentElement.nextElementSibling;
    const arrow = el.querySelector(".toggle-arrow");
    const isOpen = description.classList.contains("open");

    if (isOpen) {
        // закрытие
        const startHeight = description.scrollHeight;
        description.style.height = startHeight + "px";
        requestAnimationFrame(() => {
            description.style.height = "0";
            description.classList.remove("open");
            arrow.style.transform = "rotate(0deg)";
        });
    } else {
        // открытие
        description.classList.add("open");

        // сначала скрыто, выставляем реальную высоту
        description.style.height = "auto";
        const fullHeight = description.scrollHeight + "px";
        description.style.height = "0px";

        requestAnimationFrame(() => {
            description.style.height = fullHeight;
        });

        description.addEventListener("transitionend", () => {
            description.style.height = "auto";
        }, { once: true });

        arrow.style.transform = "rotate(180deg)";

        // 👇 автоматическая прокрутка вниз, если текст не помещается
        setTimeout(() => {
            const rect = description.getBoundingClientRect();
            const viewportBottom = window.innerHeight;
            if (rect.bottom > viewportBottom) {
                window.scrollBy({
                    top: rect.bottom - viewportBottom + 40,
                    behavior: "smooth"
                });
            }
        }, 400);
    }
}

async function addTask() {
    const title = document.getElementById("title").value.trim();
    const description = document.getElementById("description").value.trim();
    const due_time = document.getElementById("due_time").value;
    if (!title) return alert("Введите название задачи!");

    await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, description, due_time })
    });

    document.getElementById("title").value = "";
    document.getElementById("description").value = "";
    document.getElementById("due_time").value = "";
    fetchTasks();
}

async function deleteTask(id) {
    await fetch(API_URL + id, { method: "DELETE" });
    fetchTasks();
}

async function toggleComplete(id, completed) {
    const response = await fetch(API_URL + id);
    const task = await response.json();

    await fetch(API_URL + id, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            title: task.title,
            description: task.description,
            due_time: task.due_time,
            completed: completed
        })
    });
    fetchTasks();
}

document.getElementById("add-btn").addEventListener("click", addTask);
// Controls
const searchInput = document.getElementById("search");
const filterCompleted = document.getElementById("filter-completed");

function reload(resetOffset = false) {
    fetchTasks();
}

if (searchInput) searchInput.addEventListener("input", () => { queryState.search = searchInput.value.trim(); reload(true); });
if (filterCompleted) filterCompleted.addEventListener("change", () => { queryState.completed = filterCompleted.value; reload(true); });
// сортировки нет — оставили только поиск и тип

fetchTasks();

// убраны тёмная тема и 'сначала просроченные' по запросу

// Автоизменение высоты textarea описания при вводе
const descriptionInput = document.getElementById("description");
if (descriptionInput) {
    const autoResize = (el) => {
        el.style.height = "auto";
        el.style.height = el.scrollHeight + "px";
    };
    // при вводе
    descriptionInput.addEventListener("input", () => autoResize(descriptionInput));
    // при загрузке страницы (если есть сохранённый текст)
    window.addEventListener("load", () => autoResize(descriptionInput));
}

// (Статический фон задан в CSS)