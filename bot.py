import asyncio
import json
from datetime import datetime
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
        with open(TASKS_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_tasks(tasks):
    with open(TASKS_FILE, "w") as file:
        json.dump(tasks, file)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот-напоминалка. Напиши /add <текст>, чтобы сохранить задачу.")


async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    task_text = " ".join(context.args)

    if not task_text:
        await update.message.reply_text("Пожалуйста, укажи текст задачи после команды /add.")
        return

    tasks = load_tasks()
    user_tasks = tasks.get(user_id, [])
    user_tasks.append(task_text)
    tasks[user_id] = user_tasks
    save_tasks(tasks)

    await update.message.reply_text(f"Задача добавлена: {task_text}")


async def show_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    tasks = load_tasks()
    user_tasks = tasks.get(user_id, [])

    if not user_tasks:
        await update.message.reply_text("У тебя пока нет задач.")
    else:
        task_list = "\n".join(f"{i+1}. {task}" for i, task in enumerate(user_tasks))
        await update.message.reply_text(f"Твои задачи:\n{task_list}")


async def remind_tasks():
    tasks = load_tasks()
    for user_id, user_tasks in tasks.items():
        if user_tasks:
            task_list = "\n".join(f"- {task}" for task in user_tasks)
            try:
                await app.bot.send_message(chat_id=int(user_id), text=f"Напоминание о задачах:\n{task_list}")
            except Exception as e:
                print(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")


async def run_bot():
    global app
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_task))
    app.add_handler(CommandHandler("tasks", show_tasks))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(remind_tasks, CronTrigger(day_of_week="fri", hour=18, minute=0))
    scheduler.start()

    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(run_bot())
