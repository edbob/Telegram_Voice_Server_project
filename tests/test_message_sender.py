import requests
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from gtts import gTTS
from datetime import datetime
from telethon.sync import TelegramClient
from bot.config import ADMIN_ID, BOT_TOKEN, DB_URL, API_HASH, TARGET_CHAT, BOT_NAME

# === Настройки ===
TG_API_ID = ADMIN_ID        # замени на своё
TG_API_HASH = API_HASH # замени на своё
GROUP_NAME = BOT_NAME  # по необходимости
SESSION = 'test_session'

text = "🚨 Тестовая тревога для проверки системы"
source = "Test Channel"
date = datetime.utcnow().isoformat()
sender_id = 99999

# === Создание голосового файла ===
tts = gTTS(text=text, lang='ru')
voice_path_mp3 = 'test_voice.mp3'
voice_path_ogg = 'test_voice.ogg'

tts.save(voice_path_mp3)

# Конвертируем в OGG (если нужно для Telegram)
os.system(f'ffmpeg -y -i {voice_path_mp3} -ac 1 -ar 16000 -c:a libopus {voice_path_ogg}')

# === Отправка в Telegram ===
with TelegramClient(SESSION, TG_API_ID, TG_API_HASH) as client:
    entity = client.get_entity(GROUP_NAME)
    client.send_file(entity, voice_path_ogg, caption=text)

# === Отправка на Flask-сервер ===
with open(voice_path_ogg, 'rb') as f:
    response = requests.post('http://localhost:5000/upload', files={'file': f}, data={
        'message': text,
        'source': source,
        'sender_id': sender_id,
        'date': date
    })
    try:
        print("Ответ от сервера:", response.json())
    except ValueError:
        print("Сервер вернул не-JSON:", response.text)

# Удаление файлов
os.remove(voice_path_mp3)
os.remove(voice_path_ogg)
