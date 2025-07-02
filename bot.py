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
    await update.message.reply_text("Привет! Пиши /add <текст> для новой задачи.")

async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    task_text = " ".join(context.args)
    if not task_text:
        await update.message.reply_text("Напиши текст после /add.")
        return
    tasks = load_tasks()
    tasks.setdefault(user_id, []).append(task_text)
    save_tasks(tasks)
    await update.message.reply_text(f"✅ Добавлено: {task_text}")

async def show_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    tasks = load_tasks().get(user_id, [])
    if not tasks:
        await update.message.reply_text("У тебя пока нет задач.")
    else:
        await update.message.reply_text("Твои задачи:\n" +
            "\n".join(f"{i+1}. {t}" for i, t in enumerate(tasks)))

async def remind_tasks(context: ContextTypes.DEFAULT_TYPE):
    tasks = load_tasks()
    for uid, items in tasks.items():
        if items:
            text = "Напоминание:\n" + "\n".join(f"- {t}" for t in items)
            try:
                await context.bot.send_message(chat_id=int(uid), text=text)
            except Exception as e:
                print(f"Ошибка {e}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_task))
    app.add_handler(CommandHandler("tasks", show_tasks))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(remind_tasks, CronTrigger(day_of_week="fri", hour=18, minute=0), args=(app,))
    scheduler.start()

    app.run_polling()

if __name__ == "__main__":
    main()
