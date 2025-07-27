import os
import sys
import pytest
import asyncio
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import AsyncMock, patch
from bot.db import MessageDB
from bot.processor import TextProcessor
from pathlib import Path

@pytest.mark.asyncio
async def test_message_pipeline(tmp_path):
    test_db_path = tmp_path / "test_messages.db"
    db = MessageDB(str(test_db_path))

    # 1. Подготовка входных данных
    test_message = "Привет, мир!"
    test_sender_id = 12345
    test_source = "TestChannel"

    # 2. Мокаем отправку в Telegram и загрузку на сервер
    with patch("bot.processor.send_to_telegram", new=AsyncMock()) as mock_telegram, \
         patch("bot.processor.upload_to_server", new=AsyncMock(return_value="https://example.com/voice.ogg")):

        # 3. Запускаем обработку
        filename = await TextProcessor(test_sender_id, test_message, test_source)

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