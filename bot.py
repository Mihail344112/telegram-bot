import asyncio
import json
import os
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN", "вставь_сюда_твой_токен")

TASKS_FILE = "tasks.json"

def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот-задачник. Напиши задачу в формате:\n\n/задача G4F Сделать ревизию")

async def задача(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Пожалуйста, добавь текст задачи.")
        return
    блок = text.split()[0]
    описание = " ".join(text.split()[1:])
    задача = {
        "время": datetime.now().isoformat(),
        "пользователь": user,
        "блок": блок,
        "описание": описание,
    }
    tasks = load_tasks()
    tasks.append(задача)
    save_tasks(tasks)
    await update.message.reply_text(f"✅ Задача сохранена: {блок} — {описание}")

async def отчёт(context: ContextTypes.DEFAULT_TYPE):
    tasks = load_tasks()
    if not tasks:
        return
    grouped = {}
    for t in tasks:
        grouped.setdefault(t["блок"], []).append(f"{t['пользователь']}: {t['описание']}")
    текст = "\n\n".join(f"*{k}*\n" + "\n".join(v) for k, v in grouped.items())
    await context.bot.send_message(chat_id=os.getenv("CHAT_ID", ""), text=текст, parse_mode="Markdown")
    save_tasks([])  # Очистка задач после отчёта

async def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("задача", задача))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(отчёт, "cron", day_of_week="fri", hour=18, minute=0, args=[app.bot])
    scheduler.start()

    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(run_bot())
