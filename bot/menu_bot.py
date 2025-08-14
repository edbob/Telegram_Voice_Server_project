from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, ConversationHandler, filters
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from bot.weather import get_weather
from bot.config import ADMIN_ID, BOT_TOKEN, DB_URL
from bot.db import MessageDB

ADMIN_CHAT_ID = ADMIN_ID
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

async def process_action(action: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
    if action == 'msg_admin':
        context.user_data['awaiting_admin_msg'] = True
        await update.message.reply_text("✍️ Напиши сообщение, которое я передам админу.")
        return SEND_ADMIN_MESSAGE
    
    elif action == 'weather':
        weather_info = get_weather()
        await update.message.reply_text(weather_info)

    elif action == 'stats':
        db = MessageDB(DB_URL)
        text = "📊 Статистика по тревогам:\n\n"
        for period_name in ['day', 'week', 'month']:
            stats = db.get_air_alert_stats(period_name)
            text += f"🗓 За {period_name}:\n"
            text += f"  • Кол-во тревог: {stats['count']}\n"
            text += f"  • Общая длительность: {stats['total_minutes']} мин\n"
            text += f"  • Средняя длительность: {stats['avg_minutes']} мин\n"
            text += f"  • Последняя тревога: {stats['last_alert']}\n"
            text += f"  • Последний отбой: {stats['last_clear']}\n\n"

        await update.message.reply_text(text)

    elif action == 'advertise':
        await update.message.reply_text("📢 Размещение рекламы стоит 100₴. Напиши 'Да', чтобы подтвердить.")
        
    else:
        await update.message.reply_text("⚠️ Неизвестная команда. Используйте /start или кнопки.")

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    return await process_action(query.data, update, context)

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

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    
    app.add_handler(CommandHandler("weather", lambda u, c: process_action('weather', u, c)))
    app.add_handler(CommandHandler("stats", lambda u, c: process_action('stats', u, c)))
    app.add_handler(CommandHandler("advertise", lambda u, c: process_action('advertise', u, c)))
    app.add_handler(CommandHandler("msg_admin", lambda u, c: process_action('msg_admin', u, c)))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_action))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_message))

    print("🤖 Меню-бот запущен")
    app.run_polling()

if __name__ == '__main__':
    main()