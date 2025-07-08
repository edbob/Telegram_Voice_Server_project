import asyncio
from telethon import TelegramClient
from telethon.tl.types import PeerChannel
import requests

from bot.bot_main import TelegramVoiceBot

api_id = 27893983
api_hash = '7333605e802b401937e72688aeaa1ea3'
phone = '+380979493781'

# ID каналов
all_channels = [
    -1001455546058,
    -1001594135954,
    -1001302199689,
    -1001498303038,
]

db_file = 'bot/messages.db'
target_chat = -1002129469860

async def main():
    print("⏳ Получаю названия каналов через Telethon...")

    # создаем временный клиент для получения названий
    client = TelegramClient('bot_session_temp', api_id, api_hash)
    await client.start(phone=phone)

    channel_infos = []

    async for ch in client.iter_dialogs():
        try:
            print(f"🔗 Канал найден: {ch.name} (ID: {ch.id})")
            channel_infos.append((ch.name, ch.id))
        except Exception as e:
            print(f"❌ Ошибка получения информации о канале {ch.id}: {e}")
            channel_infos.append((f"Неизвестно ({ch.id})", ch.id))

    await client.disconnect()

    # выбор пользователем
    print("\nДоступные каналы:")
    for idx, (title, ch_id) in enumerate(channel_infos):
        print(f"{idx+1}: {title} (ID: {ch_id})")

    selected = int(input("Введите номер канала для прослушивания: ")) - 1
    selected_channel_id = [channel_infos[selected][1]]

    # запускаем основного бота
    bot = TelegramVoiceBot(api_id, api_hash, phone, selected_channel_id, db_file, target_chat)

    try:
        await bot.start()
    except KeyboardInterrupt:
        print("\nСкрипт остановлен.")

# запуск
if __name__ == "__main__":
    asyncio.run(main())