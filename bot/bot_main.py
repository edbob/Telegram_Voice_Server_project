import os
import asyncio
import time
from gtts import gTTS
from telethon import TelegramClient, events
from telethon.tl.types import PeerChannel
from bot.db import MessageDB
from bot.processor import TextProcessor
import datetime

class TelegramVoiceBot:
    def __init__(self, api_id, api_hash, phone, source_channels, db_file, target_chat):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.source_channels = source_channels
        self.db = MessageDB(db_file)
        self.client = TelegramClient('bot_session', api_id, api_hash)
        self.queue = asyncio.Queue()
        self.target_chat = target_chat

    async def start(self):
        await self.client.start(phone=self.phone)
        now = datetime.datetime.now().strftime('%H:%M %d.%m.%Y')
        print(f"\n✅ Бот запущен в {now} и слушает источники...")
        try:
            entities = []
            for ch_id in self.source_channels:
                entity = await self.client.get_entity(PeerChannel(ch_id))
                print(f"🔗 Канал найден: {entity.title} (ID: {entity.id})")
                entities.append(entity)
        except Exception as e:
            print(f"❌ Ошибка доступа к каналу: {e}")
            if "disk I/O error" in str(e):
                print("➡️ Проверьте права на папку сессии, свободное место на диске и не открыт ли файл сессии в другой программе.")
            return
        
        # === Обработка новых сообщений ===
        @self.client.on(events.NewMessage(chats=entities))
        async def handler(event):
            msg = event.message
            print(f"\n[{msg.date}] {msg.sender_id}: {msg.text}")

            try:
                chat = await event.get_chat()
                source = chat.title if hasattr(chat, 'title') else 'Неизвестно'
                filename = f"voice_{int(time.time())}.ogg"
            except:
                source = 'Неизвестно'

            # Сохраняем в базу
            self.db.save_message(
                sender_id=msg.sender_id,
                message=msg.text, 
                date=msg.date.isoformat(),
                source=source,
                filename=filename
            )

            clean_text = TextProcessor.clean(msg.text)
            if not clean_text.strip():
                print("⚠️ Пустой текст после очистки — пропущено.")
                return

            lang = TextProcessor.detect_lang(clean_text)
            await self.queue.put((clean_text, lang, filename))

        # === Обработка присоединений и уходов ===
        @self.client.on(events.ChatAction)
        async def membership_handler(event):
            user = await event.get_user()
            if user:
                username = f"@{user.username}" if user.username else (user.first_name or "Неизвестный")
            else:
                username = "Неизвестный"

            if event.user_joined or event.user_added:
                print(f"👋 {username} присоединился к чату.")
                await event.reply(f"Привет, {username}! Добро пожаловать 👋")
                self.db.save_stat(event.chat_id, user.id if user else 0, "joined")

            elif event.user_left or event.user_kicked:
                print(f"😢 {username} покинул чат.")
                await event.reply(f"{username}, жаль что ты покидаешь нас 😢. Что случилось?")
                self.db.save_stat(event.chat_id, user.id if user else 0, "left")

        asyncio.create_task(self.voice_worker())
        await self.client.run_until_disconnected()

    async def voice_worker(self):
        import requests
        while True:
            clean_text, lang, filename = await self.queue.get()

            tts = gTTS(text=clean_text, lang=lang, slow=False)
            mp3_path = "voice.mp3"
            ogg_path = f"voice_{int(time.time())}.ogg"

            tts.save(mp3_path)
            # Конвертация
            os.system(f'ffmpeg -y -i {mp3_path} -c:a libopus {ogg_path}')
            
            # Проверка размера файла
            if not os.path.exists(ogg_path) or os.path.getsize(ogg_path) == 0:
                print("❌ Файл ogg не создан или пустой!")
            else:
                print(f"✅ Файл ogg создан: {ogg_path}, размер: {os.path.getsize(ogg_path)} байт")

            try:
                # Отправка в Telegram .ogg с коротким текстом
                await self.client.send_file(
                    self.target_chat,
                    ogg_path,
                    voice_note=True,
                    caption=clean_text[:200]  # например до 200 символов
                )
                print("📤 Отправлено в Telegram")

                # Отправка на сервер
                with open(ogg_path, 'rb') as f:
                    try:
                        response = requests.post("http://localhost:5000/upload", files={'file': (ogg_path, f)})
                        response.raise_for_status()
                        print(f"🌍 Ответ сервера: {response.text}")
                    except requests.exceptions.RequestException as e:
                        print(f"❌ Ошибка отправки на сервер: {e}")
                        if response is not None:
                            print(f"🔁 Код ответа: {response.status_code}")
                            print(f"📦 Тело ответа: {response.text}")

            except Exception as e:
                print(f"❌ Ошибка отправки: {e}")

            finally:
                for f in (mp3_path, ogg_path):
                    if os.path.exists(f):
                        os.remove(f)

            self.queue.task_done()