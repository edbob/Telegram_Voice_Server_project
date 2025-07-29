import asyncio
from telethon import TelegramClient
import sys
import os
import asyncio
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from bot.bot_main import TelegramVoiceBot
from bot.config import ADMIN_ID, PHONE, DB_URL, API_HASH, TARGET_CHAT

api_id = ADMIN_ID
api_hash = API_HASH
phone = PHONE
db_file = DB_URL
target_chat = TARGET_CHAT

async def main():
    print("⏳ Получаю список каналов и групп через Telethon...")

    # создаем временный клиент для получения названий
    client = TelegramClient('bot_session_temp', api_id, api_hash)
    await client.start(phone=phone)

    channel_infos = []

    async for ch in client.iter_dialogs():
        if ch.is_channel or ch.is_group:
            print(f"🔗 {ch.name} (ID: {ch.id})")
            channel_infos.append((ch.name, ch.id))

    await client.disconnect()

    if not channel_infos:
        print("⚠️ Каналы не найдены.")
        return

    # выбор пользователем
    print("\n✅ Доступные каналы:")
    for idx, (title, ch_id) in enumerate(channel_infos):
        print(f"{idx+1}: {title} (ID: {ch_id})")

    try:
        selected = int(input("Введите номер канала для прослушивания: ")) - 1
        selected_channel_id = [channel_infos[selected][1]]
    except (ValueError, IndexError):
        print("❌ Некорректный выбор. Завершение.")
        return

    # запускаем основного бота
    bot = TelegramVoiceBot(api_id, api_hash, phone, selected_channel_id, db_file, target_chat)

    try:
        await bot.start()
    except asyncio.CancelledError:
        print("⚠️ Отмена выполнения (CancelledError)")
    except KeyboardInterrupt:
        print("\n⏹️ Бот остановлен пользователем (Ctrl+C)")
    finally:
        await bot.stop()
        print("🧹 Очистка завершена.")

if __name__ == "__main__":
    asyncio.run(main())
# python -m bot.telegram_bot