import json
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
import asyncio

TOKEN = "8141032644:AAHA1Ot-JvGXgXBgPrSQO609kZBjFYj9dWo"
TASKS_FILE = "tasks.json"


def загрузить_задачи():
    try:
        with open(TASKS_FILE, "r") as файл:
            return json.load(файл)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def сохранить_задачи(задачи):
    with open(TASKS_FILE, "w") as файл:
        json.dump(задачи, файл)


async def старт(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот-напоминалка. Напиши /add <текст>, чтобы сохранить задачу.")


async def добавить(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    текст_задачи = " ".join(context.args)

    if not текст_задачи:
        await update.message.reply_text("Напиши текст задачи после команды /add.")
        return

    задачи = загрузить_задачи()
    user_tasks = задачи.get(user_id, [])
    user_tasks.append(текст_задачи)
    задачи[user_id] = user_tasks
    сохранить_задачи(задачи)

    await update.message.reply_text(f"Задача добавлена: {текст_задачи}")


async def показать_задачи(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    задачи = загрузить_задачи()
    user_tasks = задачи.get(user_id, [])

    if not user_tasks:
        await update.message.reply_text("У тебя пока нет задач.")
    else:
        список = "\n".join(f"{i+1}. {task}" for i, task in enumerate(user_tasks))
        await update.message.reply_text(f"Твои задачи:\n{список}")


async def напомнить_всем(app):
    задачи = загрузить_задачи()
    for user_id, user_tasks in задачи.items():
        if user_tasks:
            список = "\n".join(f"- {task}" for task in user_tasks)
            try:
                await app.bot.send_message(chat_id=int(user_id), text=f"Напоминание о задачах:\n{список}")
            except Exception as e:
                print(f"Ошибка при отправке пользователю {user_id}: {e}")


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", старт))
    app.add_handler(CommandHandler("add", добавить))
    app.add_handler(CommandHandler("tasks", показать_задачи))

    планировщик = AsyncIOScheduler()
    планировщик.add_job(lambda: asyncio.create_task(напомнить_всем(app)), CronTrigger(day_of_week="fri", hour=18, minute=0))
    планировщик.start()

    app.run_polling()


if __name__ == "__main__":
    main()
