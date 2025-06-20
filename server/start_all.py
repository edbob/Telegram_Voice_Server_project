import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bot.bot_main import TelegramVoiceBot
import asyncio
from multiprocessing import Process
from server.app import app

def run_bot():
    api_id = int(os.environ['27893983'])
    api_hash = os.environ['7333605e802b401937e72688aeaa1ea3']
    phone = os.environ['+380979493781']
    target_chat = int(os.environ['-1002129469860'])
    source_channels = list(map(int, os.environ['-1001455546058, -1001594135954, -1001302199689, -1001498303038'].split(',')))

    bot = TelegramVoiceBot(api_id, api_hash, phone, source_channels, target_chat)
    asyncio.run(bot.start())

def run_server():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    Process(target=run_bot).start()
    run_server()