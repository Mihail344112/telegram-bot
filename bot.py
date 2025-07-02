import json
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

TOKEN = "8141032644:AAHA1Ot-JvGXgXBgPrSQO609kZBjFYj9dWo"
TASKS_FILE = "tasks.json"

def load_tasks():
    try:
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f)

async def start_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Напиши /add <текст>")

async def add_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = str(update.message.from_user.id)
    text = " ".join(ctx.args)
    if not text:
        return await update.message.reply_text("Добавь текст после /add")
    tasks = load_tasks()
    tasks.setdefault(user, []).append(text)
    save_tasks(tasks)
    await update.message.reply_text(f"Задача добавлена: {text}")

async def tasks_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = str(update.message.from_user.id)
    tasks = load_tasks().get(user, [])
    if not tasks:
        return await update.message.reply_text("Нет задач")
    lines = "\n".join(f"{i+1}. {t}" for i, t in enumerate(tasks))
    await update.message.reply_text(f"Твои задачи:\n{lines}")

async def remind(app):
    tasks = load_tasks()
    for user, lst in tasks.items():
        if lst:
            text = "Напоминание:\n" + "\n".join(f"- {t}" for t in lst)
            try:
                await app.bot.send_message(chat_id=int(user), text=text)
            except:
                pass

async def post_init(app):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(lambda: remind(app), CronTrigger(day_of_week="fri", hour=18, minute=0))
    scheduler.start()

def main():
    app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("add", add_cmd))
    app.add_handler(CommandHandler("tasks", tasks_cmd))
    app.run_polling()

if __name__ == "__main__":
    main()
