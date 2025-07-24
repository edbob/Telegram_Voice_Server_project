import asyncio
from telethon import TelegramClient
from bot.bot_main import TelegramVoiceBot
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

api_id = 27893983
api_hash = '7333605e802b401937e72688aeaa1ea3'
phone = '+380979493781'

db_file = 'bot/messages.db'
target_chat = -1002129469860

async def main():
    print("⏳ Получаю список каналов и групп через Telethon...")

    # создаем временный клиент для получения названий
    client = TelegramClient('bot_session_temp', api_id, api_hash)
    await client.start(phone=phone)

    channel_infos = []

    async for ch in client.iter_dialogs():
        if not ch.is_channel:
            continue
        print(f"🔗 {ch.name} (ID: {ch.id})")
        channel_infos.append((ch.name, ch.id))

    await client.disconnect()

    if not channel_infos:
        print("⚠️ Каналы не найдены.")
        return

    # выбор пользователем
    print("\nДоступные каналы:")
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
    except KeyboardInterrupt:
        print("\n⏹️ Бот остановлен пользователем (Ctrl+C)")

if __name__ == "__main__":
    asyncio.run(main())
# python -m bot.telegram_bot