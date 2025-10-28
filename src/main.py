from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from src.api import Task
from src.database import Base, engine, ensure_column
from src.notifications import start_notifications_background, notify_startup

app = FastAPI(title="ToDo List API")

Base.metadata.create_all(bind=engine)
ensure_column(engine, "tasks", "due_time", "TEXT")
ensure_column(engine, "tasks", "notified_60", "INTEGER DEFAULT 0")
ensure_column(engine, "tasks", "notified_5", "INTEGER DEFAULT 0")

# Подключаем API
app.include_router(Task.router)

# Подключаем статику и шаблоны
app.mount("/static", StaticFiles(directory="src/static"), name="static")
templates = Jinja2Templates(directory="src/templates")

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.on_event("startup")
async def on_startup():
    await start_notifications_background()
    await notify_startup()
