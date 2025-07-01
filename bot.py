import json
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler

TOKEN = "твой_токен_бота"  # ЗАМЕНИ на свой токен

tasks = {
    "Семья": [],
    "G4F": [],
    "ИИ": [],
    "Chef.Expert": []
}
user_state = {}

# Загрузка задач из файла, если есть
try:
    with open("tasks.json", "r", encoding="utf-8") as f:
        tasks.update(json.load(f))
except FileNotFoundError:
    pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я помогу тебе с задачами. Напиши /add чтобы добавить задачу.")

async def focus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🎯 Фокус на неделю:\n"
    for block, items in tasks.items():
        if items:
            text += f"\n{block}:\n" + "\n".join([f"- {item}" for item in items]) + "\n"
    await update.message.reply_text(text or "Пока нет задач.")

async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Семья", callback_data='Семья'),
         InlineKeyboardButton("G4F", callback_data='G4F')],
        [InlineKeyboardButton("ИИ", callback_data='ИИ'),
         InlineKeyboardButton("Chef.Expert", callback_data='Chef.Expert')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("В какой блок добавить задачу?", reply_markup=reply_markup)

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
        await update.message.reply_text("Напиши /add и выбери блок.")

async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📋 Все задачи:\n"
    for block, items in tasks.items():
        if items:
            text += f"\n{block}:\n" + "\n".join([f"- {item}" for item in items]) + "\n"
    await update.message.reply_text(text or "Задач нет.")

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await focus(update, context)

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for key in tasks:
        tasks[key] = []
    with open("tasks.json", "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
    await update.message.reply_text("🧹 Все задачи очищены.")

async def scheduled_report(app):
    for chat_id in user_state:
        response = "🗓 Автоотчёт за неделю:\n"
        for block, items in tasks.items():
            if items:
                response += f"\n{block}:\n" + "\n".join([f"- {item}" for item in items]) + "\n"
        await app.bot.send_message(chat_id=chat_id, text=response.strip() or "Пока задач нет.")

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
    scheduler.add_job(lambda: scheduled_report(app), 'cron', day_of_week='fri', hour=18, minute=0)
    scheduler.start()

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(run_bot())
