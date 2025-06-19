import os
import asyncio
import time
from gtts import gTTS
from telethon import TelegramClient, events
from telethon.tl.types import PeerChannel
from bot.db import MessageDB
from bot.processor import TextProcessor

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
        print("\nБот запущен и слушает источники...")

        try:
            entities = []
            for ch_id in self.source_channels:
                entity = await self.client.get_entity(PeerChannel(ch_id))
                print(f"🔗 Канал найден: {entity.title} (ID: {entity.id})")
                entities.append(entity)
        except Exception as e:
            print(f"Ошибка доступа к каналу: {e}")
            return

        @self.client.on(events.NewMessage(chats=entities))
        # Обработка новых сообщений
        async def handler(event):
            msg = event.message
            print(f"\n[{msg.date}] {msg.sender_id}: {msg.text}")
            
            # Получаем источник — название группы/канала
            try:
                chat = await event.get_chat()
                source = chat.title if hasattr(chat, 'title') else 'Неизвестно'
            except:
                source = 'Неизвестно'

            # Сохраняем в базу
            self.db.save_message(
                sender_id=msg.sender_id,
                message=msg.text,
                date=msg.date.isoformat(),
                source=source
                )

            clean_text = TextProcessor.clean(msg.text)
            if not clean_text.strip():
                print("Пустой текст после очистки — пропущено.")
                return

            lang = TextProcessor.detect_lang(clean_text)
            await self.queue.put((clean_text, lang, source, msg.sender_id, msg.date.isoformat()))

        asyncio.create_task(self.voice_worker())
        await self.client.run_until_disconnected()

async def voice_worker(self):
    import requests

    while True:
        clean_text, lang, source, sender_id, date = await self.queue.get()

        tts = gTTS(text=clean_text, lang=lang, slow=False)
        mp3_path = "voice.mp3"
        ogg_path = f"voice_{int(time.time())}.ogg"

        tts.save(mp3_path)
        os.system(f'ffmpeg -y -i {mp3_path} -c:a libopus {ogg_path}')

        if not os.path.exists(ogg_path) or os.path.getsize(ogg_path) == 0:
            print("❌ OGG не создан")
        else:
            try:
                await self.client.send_file(self.target_chat, ogg_path, voice_note=True)
                print("Отправлено в Telegram")

                # ⬇ Отправка на сервер
                with open(ogg_path, 'rb') as f:
                    requests.post("http://localhost:5000/upload", files={'file': (ogg_path, f)})

                # ⬇ Сохраняем в БД
                filename = ogg_path.split('/')[-1]
                self.db.save_message(
                    sender_id=sender_id,
                    message=clean_text,
                    date=date,
                    source=source,
                    filename=filename
                )

            except Exception as e:
                print("Ошибка при отправке:", e)

            finally:
                os.remove(mp3_path)
                os.remove(ogg_path)

        self.queue.task_done()