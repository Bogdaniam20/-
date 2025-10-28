## To-Do List API (FastAPI)

Простое учебное приложение «To-Do List» на FastAPI + SQLAlchemy + SQLite с минимальным UI (Jinja2), статикой и фоновыми уведомлениями в Telegram.

### Возможности
- **CRUD задач**: создание, чтение списка и отдельной записи, обновление, удаление
- **Фильтрация**: `completed`, `has_due`, `search`
- **Сортировка**: `sort_by` = `created|title|due|id`, `order` = `asc|desc`
- **Пагинация**: `limit` (1–500), `offset` (≥0)
- **UI**: страница по `/` для ручной работы со списком
- **Уведомления**: Telegram-бот напоминает за 60 минут и за 5 минут до срока (`due_time`)

### Технологии
- Python 3.11+
- FastAPI, Uvicorn
- SQLAlchemy (ORM), SQLite
- Pydantic
- httpx (Telegram)
- Jinja2, StaticFiles

---

## Установка и запуск

### 1) Клонирование и окружение
```powershell
git clone <repo-url>
cd To_Do
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Установка зависимостей
```powershell
pip install fastapi uvicorn sqlalchemy pydantic httpx jinja2
```

### 3) Запуск сервера
```powershell
uvicorn src.main:app --reload
```

Сервер поднимется на `http://127.0.0.1:8000`:
- UI: `http://127.0.0.1:8000/`
- OpenAPI/Swagger: `http://127.0.0.1:8000/docs`

База `todo.db` создаётся автоматически. Также при старте добавляются отсутствующие колонки: `due_time`, `notified_60`, `notified_5`.

---

## Конфигурация уведомлений в Telegram (опционально)
Фоновая задача периодически проверяет невыполненные задачи с `due_time` и шлёт напоминания:
- за ~60 минут
- за ~5 минут

В файле `src/notifications.py` задаётся токен бота в константе `TELEGRAM_TOKEN`.

Шаги настройки:
1. Создайте бота в `@BotFather` и вставьте токен в `src/notifications.py` вместо текущего значения `TELEGRAM_TOKEN`.
2. Запустите сервер и напишите любое сообщение вашему боту из Telegram-клиента.
3. Приложение автоматически прочитает `chat_id` через `getUpdates` и сохранит в таблицу `settings` в SQLite.

Примечание: токен хранится в коде для простоты учебного проекта. Для реальных проектов храните секреты в переменных окружения/Secret Manager.

---

## Структура проекта
```
To_Do/
  src/
    api/Task.py          # эндпойнты /tasks
    models/Task.py       # ORM-модель Task
    schemas/Task.py      # Pydantic-схемы
    database.py          # Engine, Session, ensure_column
    notifications.py     # фоновые уведомления Telegram
    main.py              # FastAPI app, маршруты, статика и шаблоны
    static/              # стили, скрипты, изображения
    templates/index.html # UI
  test_main.http         # готовые HTTP-запросы для ручной прогона
  TEST_PLAN.md           # тест-план
  TEST_RESULTS_TEMPLATE.md # шаблон отчёта о тестировании
  todo.db                # SQLite БД (создаётся при старте)
```

---

## API

Базовый URL: `http://127.0.0.1:8000`

### Модель Task (ответ)
```json
{
  "id": 1,
  "title": "string",
  "description": "string|null",
  "completed": false,
  "due_time": "YYYY-MM-DDTHH:MM | YYYY-MM-DD HH:MM",
  "notified_60": false,
  "notified_5": false
}
```

### POST /tasks
Создать задачу.

Тело запроса:
```json
{
  "title": "string",
  "description": "string|null",
  "due_time": "2025-10-28T12:00"
}
```

### GET /tasks
Список задач с фильтрами/сортировкой/пагинацией.

Параметры запроса:
- `completed`: true|false
- `has_due`: true|false
- `search`: строка поиска по `title`/`description`
- `sort_by`: created|title|due|id (неизвестное значение → применяется значение по умолчанию)
- `order`: asc|desc (неизвестное значение → asc)
- `limit`: 1..500 (невалидные значения → 422)
- `offset`: ≥0 (невалидные значения → 422)

### GET /tasks/{id}
Получить задачу по идентификатору (404, если не существует).

### PUT /tasks/{id}
Обновить поля задачи (404, если не существует). Поддерживаются изменения `title`, `description`, `due_time`, `completed`, `notified_60`, `notified_5`.

### DELETE /tasks/{id}
Удалить задачу (404, если не существует).

---

## Примеры запросов (cURL)
```bash
# Создать
curl -X POST http://127.0.0.1:8000/tasks/ \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","description":"Demo","due_time":"2025-10-28T12:00"}'

# Список (выполненные, сортировка по title desc, страница 2x2)
curl "http://127.0.0.1:8000/tasks?completed=true&sort_by=title&order=desc&limit=2&offset=2"

# Получить одну
curl http://127.0.0.1:8000/tasks/1

# Обновить
curl -X PUT http://127.0.0.1:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"completed":true}'

# Удалить
curl -X DELETE http://127.0.0.1:8000/tasks/1
```

---

## Тестирование
- См. `TEST_PLAN.md` — содержит полный перечень тест-кейсов (позитивные/негативные)
- Для ручного прогона используйте `test_main.http` в IDE или Postman/cURL
- Для фиксации результатов — заполните `TEST_RESULTS_TEMPLATE.md`

> Замечание: в учебном режиме допускается ручной прогон. Легко расширить проект автотестами на Pytest.

---

## Сброс БД
Чтобы начать «с чистого листа», остановите сервер и удалите файл `todo.db`:
```powershell
Remove-Item .\todo.db
```
При следующем старте БД будет создана заново.

---

## Ограничения и заметки безопасности
- В проекте **нет аутентификации/авторизации**
- Telegram-токен в коде — для упрощения демонстрации. Не храните секреты в репозитории
- Поле `created` явно не хранится — используется `id` как прокси для сортировки по созданию

---

## Лицензия
Учебный проект. Используйте свободно на свой страх и риск.


