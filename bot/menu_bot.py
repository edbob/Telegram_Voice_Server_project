from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, ConversationHandler, filters
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from bot.weather import get_weather


ADMIN_CHAT_ID = 27893983  # Telegram ID
# Состояние для отправки сообщения админу
SEND_ADMIN_MESSAGE = range(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📬 Сообщение админу", callback_data='msg_admin')],
        [InlineKeyboardButton("🌤 Погода", callback_data='weather')],
        [InlineKeyboardButton("📊 Статистика", callback_data='stats')],
        [InlineKeyboardButton("📢 Разместить рекламу", callback_data='advertise')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👋 Привет! Выбери действие:", reply_markup=reply_markup)

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'msg_admin':
        context.user_data['awaiting_admin_msg'] = True
        await query.message.reply_text("✍️ Напиши сообщение, которое я передам админу.")
        return SEND_ADMIN_MESSAGE
    
    elif query.data == 'weather':
        weather_info = get_weather()
        await query.message.reply_text(weather_info)
    elif query.data == 'stats':
        await query.message.reply_text("📊 За сегодня: 123 сообщения\n(в будущем будет график).")
    elif query.data == 'advertise':
        await query.message.reply_text("📢 Размещение рекламы стоит 100₴. Напиши 'Да', чтобы подтвердить.")

# === Обработка текста от пользователя ===
async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    msg = f"📨 Сообщение от @{user.username or user.first_name} (ID: {user.id}):\n\n{text}"
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg)
    await update.message.reply_text("✅ Сообщение отправлено админу.")
    return ConversationHandler.END

# === Отмена ===
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Действие отменено.")
    return ConversationHandler.END

def main():
    from telegram.ext import ApplicationBuilder

    TOKEN = "7152007094:AAE3yHERr4WuVMvkLa-inKQL1xQsqFN0fmQ" # Токен бота

    app = ApplicationBuilder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_button)],
        states={
            SEND_ADMIN_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_message)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_message))

    print("🤖 Меню-бот запущен")
    app.run_polling()

if __name__ == '__main__':
    main()