import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import json
import os

TOKEN = os.getenv("8141032644:AAHA1Ot-JvGXgXBgPrSQO609kZBjFYj9dWo")

TASKS_FILE = "tasks.json"

def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r") as file:
            return json.load(file)
    return {}

def save_tasks(tasks):
    with open(TASKS_FILE, "w") as file:
        json.dump(tasks, file, indent=4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот для задач.")

async def задача(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.username or update.effective_user.id
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Добавь текст задачи после команды.")
        return
    tasks = load_tasks()
    tasks.setdefault(user, []).append(text)
    save_tasks(tasks)
    await update.message.reply_text(f"Задача сохранена: {text}")

async def send_report(app):
    tasks = load_tasks()
    for user, user_tasks in tasks.items():
        try:
            await app.bot.send_message(
                chat_id=f"@{user}" if isinstance(user, str) else user,
                text="📝 Твои задачи за неделю:\n" + "\n".join(f"– {t}" for t in user_tasks),
            )
        except Exception as e:
            print(f"Не удалось отправить {user}: {e}")
    save_tasks({})  # очищаем после отчёта

async def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("задача", задача))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_report, CronTrigger(day_of_week="fri", hour=18, minute=0), args=[app])
    scheduler.start()

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(run_bot())
