from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import json
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, time
import asyncio

# 🔐 ВСТАВЬ СЮДА СВОЙ ТОКЕН
TOKEN = '8141032644:AAHA1Ot-JvGXgXBgPrSQO609kZBjFYj9dWo'

# 📂 Загружаем задачи из файла или создаём
tasks = {
    "Семья": [],
    "G4F": [],
    "ИИ": [],
    "Chef.Expert": []
}

if os.path.exists("tasks.json"):
    with open("tasks.json", "r", encoding="utf-8") as f:
        tasks.update(json.load(f))

# 🧠 Временное состояние
user_state = {}

# 🟢 Команды
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_state[update.message.from_user.id] = "init"
    await update.message.reply_text("Привет! Я твой ассистент. Введи /focus, /add, /list, /report, /clear")

async def focus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введи фокус на неделю по блокам: Семья / G4F / ИИ / Chef.Expert")

async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = "📋 Текущие задачи:\n"
    for block, items in tasks.items():
        response += f"\n{block}:\n" + ("\n".join([f"— {item}" for item in items]) if items else "(пусто)")
    await update.message.reply_text(response)

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = "📝 Отчёт за неделю:\n"
    for block, items in tasks.items():
        if items:
            response += f"\n{block}:\n" + "\n".join([f"- {item}" for item in items]) + "\n"
    await update.message.reply_text(response if response.strip() != "📝 Отчёт за неделю:" else "Пока задач нет.")

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for block in tasks:
        tasks[block] = []
    with open("tasks.json", "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
    await update.message.reply_text("🧹 Все задачи очищены.")

async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Семья", callback_data='Семья'), InlineKeyboardButton("G4F", callback_data='G4F')],
        [InlineKeyboardButton("ИИ", callback_data='ИИ'), InlineKeyboardButton("Chef.Expert", callback_data='Chef.Expert')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📍 В какой блок добавить задачу?", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    block = query.data
    user_state[user_id] = block
    await query.message.reply_text(f"Что добавить в {block}?")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in user_state and user_state[user_id] != "init":
        block = user_state.pop(user_id)
        tasks[block].append(update.message.text)
        with open("tasks.json", "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
        await update.message.reply_text(f"✅ Добавлено в {block}: {update.message.text}")
    else:
        await update.message.reply_text("Напиши /add и выбери блок для добавления задачи.")

# 🚀 Основной запуск с планировщиком
async def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("focus", focus))
    app.add_handler(CommandHandler("add", add_task))
    app.add_handler(CommandHandler("list", list_tasks))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    scheduler = AsyncIOScheduler()

    async def scheduled_report():
        for chat_id in user_state:
            response = "📝 Автоотчёт за неделю:\n"
            for block, items in tasks.items():
                if items:
                    response += f"\n{block}:\n" + "\n".join([f"- {item}" for item in items]) + "\n"
            await app.bot.send_message(chat_id=chat_id, text=response if response.strip() != "📝 Автоотчёт за неделю:" else "Пока задач нет.")

    scheduler.add_job(scheduled_report, 'cron', day_of_week='fri', hour=18, minute=0)
    scheduler.start()

    await app.initialize()
    await app.start()
    print("Бот запущен. Нажми Ctrl+C для остановки.")
    while True:
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(run_bot())
