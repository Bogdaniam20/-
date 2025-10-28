from datetime import datetime
import asyncio
import httpx
from sqlalchemy.orm import Session
from src.database import SessionLocal, engine

TELEGRAM_TOKEN = "8348163353:AAHvr-2isZC8DkMmdY4-1lPSt58L5-X8YCc"
API_BASE = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# create simple settings table to store chat_id
try:
	with engine.connect() as conn:
		conn.exec_driver_sql("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
except Exception:
	pass

SETTINGS_KEY_CHAT = "chat_id"

async def get_chat_id(client: httpx.AsyncClient) -> int | None:
	# Try to read from DB
	with engine.connect() as conn:
		res = conn.exec_driver_sql("SELECT value FROM settings WHERE key='chat_id'").fetchone()
		if res and res[0]:
			return int(res[0])
	# Fallback: poll getUpdates and save first chat
	try:
		r = await client.get(f"{API_BASE}/getUpdates", timeout=10)
		r.raise_for_status()
		data = r.json()
		for upd in data.get("result", []):
			msg = upd.get("message") or upd.get("edited_message")
			if msg and "chat" in msg:
				chat_id = msg["chat"]["id"]
				with engine.connect() as conn:
					conn.exec_driver_sql("INSERT OR REPLACE INTO settings (key, value) VALUES ('chat_id', ?)", (str(chat_id),))
				return int(chat_id)
	except Exception:
		return None
	return None

async def send_message(client: httpx.AsyncClient, chat_id: int, text: str) -> None:
	try:
		await client.post(f"{API_BASE}/sendMessage", json={"chat_id": chat_id, "text": text}, timeout=10)
	except Exception:
		pass

async def check_and_notify_loop():
	async with httpx.AsyncClient() as client:
		while True:
			chat_id = await get_chat_id(client)
			if chat_id:
				try:
					with SessionLocal() as db:
						from src.models.Task import Task as TaskModel
						# используем локальное время без таймзоны, как и в datetime-local
						now = datetime.now()
						tasks = db.query(TaskModel).filter(TaskModel.completed == False, TaskModel.due_time != None).all()
						for t in tasks:
							try:
								# Parse stored due_time; support naive local datetime-local string
								due_str = (t.due_time or "").strip()
								if not due_str:
									continue
								# Parse common formats from input type="datetime-local"
								parsed = None
								for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
									try:
										parsed = datetime.strptime(due_str, fmt)
										break
									except Exception:
										continue
								if parsed is None:
									# last resort
									try:
										due = datetime.fromisoformat(due_str)
									except Exception:
										continue
								else:
									due = parsed
								delta_minutes = int((due - now).total_seconds() // 60)
								# Простая диагностика состояния (не спамит в чат)
								# print(f"[notify] {t.title}: now={now}, due={due}, delta_min={delta_minutes}, n60={t.notified_60}, n5={t.notified_5}")
								# use 1-minute windows to avoid missing due to scheduling drift
								if 59 <= delta_minutes <= 60 and not t.notified_60:
									await send_message(client, chat_id, f"Через 1 час срок задачи: {t.title}")
									t.notified_60 = True
								if 4 <= delta_minutes <= 5 and not t.notified_5:
									await send_message(client, chat_id, f"Через 5 минут срок задачи: {t.title}")
									t.notified_5 = True
							except Exception:
								continue
						db.commit()
				except Exception:
					pass
			await asyncio.sleep(60)

# Entrypoint to start from FastAPI startup
async def start_notifications_background():
	asyncio.create_task(check_and_notify_loop())

async def notify_startup():
	async with httpx.AsyncClient() as client:
		chat_id = await get_chat_id(client)
		if chat_id:
			await send_message(client, chat_id, "Сервер запущен")
