from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import logging

# Токен бота
TOKEN = "8141032644:AAHA1Ot-JvGXgXBgPrSQO609kZBjFYj9dWo"

# Логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Хранилище задач (в памяти)
tasks = []
waiting_for_task = set()

# Стартовая команда
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("➕ Добавить задачу", callback_data='add_task')],
        [InlineKeyboardButton("📋 Показать задачи", callback_data='show_tasks')],
        [InlineKeyboardButton("❌ Очистить задачи", callback_data='clear_tasks')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет! Выбери действие:", reply_markup=reply_markup)

# Обработка кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "add_task":
        waiting_for_task.add(user_id)
        await query.edit_message_text("✍️ Напиши задачу одним сообщением.")

    elif query.data == "show_tasks":
        if tasks:
            task_list = "\n".join(f"{i+1}. {t}" for i, t in enumerate(tasks))
            await query.edit_message_text(f"📋 Текущие задачи:\n{task_list}")
        else:
            await query.edit_message_text("📋 Список задач пуст.")

    elif query.data == "clear_tasks":
        tasks.clear()
        await query.edit_message_text("✅ Все задачи удалены.")

# Обработка сообщений с задачами
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in waiting_for_task:
        task_text = update.message.text
        tasks.append(task_text)
        waiting_for_task.remove(user_id)
        await update.message.reply_text("📝 Задача добавлена.")
    else:
        await update.message.reply_text("Напиши /start, чтобы выбрать действие.")

# Запуск приложения
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    app.run_polling()
