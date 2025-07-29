import os
import sys
import pytest
import asyncio
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import AsyncMock, patch
from bot.db import MessageDB
from bot.processor import TextProcessor
from bot.bot_main import TelegramVoiceBot
from pathlib import Path
from bot.config import ADMIN_ID, PHONE, DB_URL, API_HASH, TARGET_CHAT

class TestSendMessageInTelegram:
    @pytest.fixture
    def bot(self):
        return TelegramVoiceBot(ADMIN_ID, API_HASH, PHONE, [TARGET_CHAT], DB_URL, TARGET_CHAT)

    @pytest.mark.asyncio
    async def test_send_message(self, bot):
        with patch.object(bot.client, 'send_message', new=AsyncMock()) as mock_send:
            await bot.send_message("Test message")
            mock_send.assert_called_once_with(TARGET_CHAT, "Test message")

    @pytest.mark.asyncio
    async def test_message_pipeline(tmp_path):
        test_db_path = tmp_path / "test_messages.db"
        db = MessageDB(str(test_db_path))

        # 1. Подготовка входных данных
        test_message = "Привет, мир!"
        test_sender_id = ADMIN_ID
        test_source = TARGET_CHAT

        # 2. Мокаем отправку в Telegram и загрузку на сервер
        with patch("bot.processor.send_to_telegram", new=AsyncMock()) as mock_telegram, \
            patch("bot.processor.upload_to_server", new=AsyncMock(return_value="https://example.com/voice.ogg")):

            # 3. Запускаем обработку
            filename = await TextProcessor(test_message)

            # 4. Проверка: файл должен быть создан
            file_path = Path("uploads") / filename
            assert file_path.exists(), f"Файл не найден: {file_path}"

            # 5. Проверка: запись в БД
            messages = db.get_latest_messages(1)
            assert messages[0]['message'] == test_message
            assert messages[0]['filename'] == str(filename)

            # 6. Проверка: отправка в телеграм была вызвана
            mock_telegram.assert_called_once()

            # 7. Проверка: файл был "загружен" на сервер
            mock_telegram.assert_called_once()
        
if __name__ == "__main__":
    pytest.main()