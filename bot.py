import asyncio
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

TOKEN = "8141032644:AAHA1Ot-JvGXgXBgPrSQO609kZBjFYj9dWo"
TASKS_FILE = "tasks.json"

def load_tasks():
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_tasks(tasks):
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот-напоминалка. Используй /добавить <текст>")

async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = str(update.effective_user.id)
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Введите текст после команды.")
        return
    tasks = load_tasks()
    tasks.setdefault(user, []).append(text)
    save_tasks(tasks)
    await update.message.reply_text(f"Задача сохранена: {text}")

async def show_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = str(update.effective_user.id)
    tasks = load_tasks().get(user, [])
    if not tasks:
        await update.message.reply_text("Задач нет.")
    else:
        msg = "\n".join(f"{i+1}. {t}" for i, t in enumerate(tasks))
        await update.message.reply_text(f"Твои задачи:\n{msg}")

async def send_reminders(app):
    tasks = load_tasks()
    for user, user_tasks in tasks.items():
        if user_tasks:
            msg = "\n".join(f"- {t}" for t in user_tasks)
            await app.bot.send_message(chat_id=int(user), text=f"Напоминание:\n{msg}")

async def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("добавить", add_task))
    app.add_handler(CommandHandler("задачи", show_tasks))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_reminders, CronTrigger(day_of_week="fri", hour=18, minute=0), args=[app])
    scheduler.start()

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(run_bot())
