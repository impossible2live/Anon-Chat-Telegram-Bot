import logging
from telegram import (
    ReplyKeyboardMarkup,
    Update,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
waiting_users = []
active_chats = {}
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard1 = [["🔍 Поиск собеседника", "🛑 Стоп", "➡️ Следующий"]]
    await update.message.reply_text("Что вы хотите?", reply_markup=ReplyKeyboardMarkup(
            keyboard1, resize_keyboard=True))

async def find(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id in waiting_users:
        await update.message.reply_text("Вы уже ищите собеседника")
        return
    if waiting_users:
        partner_id = waiting_users.pop(0)
        active_chats[user_id] = partner_id
        active_chats[partner_id] = user_id
        await update.message.reply_text("✅ Собеседник найден!")
        await context.bot.send_message(partner_id, "✅ Собеседник найден!")
    else:
        waiting_users.append(user_id)
        await update.message.reply_text("⌛ Ищем вам собеседника...")
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        await context.bot.send_message(partner_id, update.message.text)
    else:
        await update.message.reply_text("Собеседник еще не найден")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id in waiting_users:
        waiting_users.remove(user_id)
        await update.message.reply_text("Поиск остановлен")
    elif user_id in active_chats:
        partner_id = active_chats.pop(user_id)
        active_chats.pop(partner_id, None)
        await update.message.reply_text("Вы закончили общение")
        await context.bot.send_message(partner_id, "Ваш собеседник закончил общение 😔")
    else:
        await update.message.reply_text("Чтобы начать общение нажмите 🔍 Поиск собеседника")

async def next(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await stop(update, context)
    await find(update, context)

def main() -> None:
    application = Application.builder().token("TOKEN").build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex("^(🔍 Поиск собеседника)$"), find))
    application.add_handler(MessageHandler(filters.Regex("^(🛑 Стоп)$"), stop))
    application.add_handler(MessageHandler(filters.Regex("^(➡️ Следующий)$"), next))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
