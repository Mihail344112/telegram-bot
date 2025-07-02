import json
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)

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
    await update.message.reply_text("Привет! /add <текст> — сохранить задачу; /tasks — список.")

async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Пиши после /add текст задачи.")
        return
    uid = str(update.effective_user.id)
    tasks = load_tasks()
    tasks.setdefault(uid, []).append(text)
    save_tasks(tasks)
    await update.message.reply_text(f"Задача добавлена.")

async def show_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    tasks = load_tasks().get(uid, [])
    if not tasks:
        await update.message.reply_text("Задач нет.")
    else:
        await update.message.reply_text("\n".join(f"{i+1}. {t}" for i, t in enumerate(tasks)))

async def remind_tasks(app):
    tasks = load_tasks()
    for uid, lst in tasks.items():
        if lst:
            text = "Напоминание:\n" + "\n".join(f"- {t}" for t in lst)
            try:
                await app.bot.send_message(chat_id=int(uid), text=text)
            except:
                pass

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_task))
    app.add_handler(CommandHandler("tasks", show_tasks))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(lambda: remind_tasks(app), CronTrigger(day_of_week="fri", hour=18, minute=0))
    scheduler.start()

    app.run_polling()

if __name__ == "__main__":
    main()
