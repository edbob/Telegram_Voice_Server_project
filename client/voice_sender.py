import requests
from gtts import gTTS
import os

def send_voice_message(text, lang='ru'):
    tts = gTTS(text=text, lang=lang)
    voice_path = 'voice.mp3'
    tts.save(voice_path)

    url = 'http://localhost:5000/upload'
    files = {'voice': open(voice_path, 'rb')}
    data = {'text': text}
    response = requests.post(url, files=files, data=data)
    print("Ответ сервера:", response.json())

    os.remove(voice_path)

if __name__ == '__main__':
    send_voice_message("Привет! Это проверка.")