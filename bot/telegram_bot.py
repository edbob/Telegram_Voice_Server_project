import asyncio
import os
import requests

from bot.bot_main import TelegramVoiceBot

# Переменные из окружения или по умолчанию
api_id = int(os.environ.get('API_ID', 27893983))
api_hash = os.environ.get('API_HASH', '7333605e802b401937e72688aeaa1ea3')
phone = os.environ.get('BOT_PHONE', '+380979493781')

source_channels = list(map(int, os.environ.get('SOURCE_CHANNELS', '-1001455546058,-1001594135954,-1001302199689,-1001498303038').split(',')))
target_chat = int(os.environ.get('TARGET_CHAT', '-1002129469860'))
db_file = os.environ.get('DB_FILE', 'bot/messages.db')

# Создаём объект, который можно импортировать
bot = TelegramVoiceBot(api_id, api_hash, phone, source_channels, db_file, target_chat)

# Только при локальном запуске
if __name__ == "__main__":
    try:
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        print("\nСкрипт остановлен.")

    try:
        ogg_path = 'bot/voice.ogg'
        with open(ogg_path, 'rb') as f:
            response = requests.post("http://localhost:5000/upload", files={'file': f})
            print(f"Загружено на сервер: {response.text}")
    except Exception as e:
        print(f"Ошибка отправки на сервер: {e}")

# для запуска скрипта используйте команду
# python -m bot.telegram_bot