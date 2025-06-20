import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bot.bot_main import TelegramVoiceBot
import asyncio
from multiprocessing import Process
from server.app import app

def run_bot():
    api_id = int(os.environ['API_ID'])
    api_hash = os.environ['API_HASH']
    phone = os.environ['PHONE']
    target_chat = int(os.environ['TARGET_CHAT'])
    source_channels = list(map(int, os.environ['SOURCE_CHANNELS'].split(',')))


    bot = TelegramVoiceBot(api_id, api_hash, phone, source_channels, target_chat)
    asyncio.run(bot.start())

if __name__ == "__main__":
    Process(target=run_bot).start()