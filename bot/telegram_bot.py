import asyncio
import requests

from bot.bot_main import TelegramVoiceBot

if __name__ == "__main__":
    
    api_id = 27893983
    api_hash = '7333605e802b401937e72688aeaa1ea3'
    phone = '+380979493781'

    source_channels = [
        -1001455546058,
        -1001594135954,
        -1001302199689,
        -1001498303038,
    ]
    db_file = 'bot/messages.db'
    target_chat = -1002129469860

    bot = TelegramVoiceBot(api_id, api_hash, phone, source_channels, db_file, target_chat)

    try:
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        print("\nСкрипт остановлен.")
    
    try:
        ogg_path = 'bot/voice.ogg'
        # Отправка файла на сервер
        with open(ogg_path, 'rb') as f:
            response = requests.post("http://localhost:5000/upload", files={'file': f})
            print(f"Загружено на сервер: {response.text}")
    except Exception as e:
        print(f"Ошибка отправки на сервер: {e}")
        
# для запуска скрипта используйте команду
# python -m bot.telegram_bot
