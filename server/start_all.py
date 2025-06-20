from multiprocessing import Process
import asyncio
from bot.bot_main import TelegramVoiceBot
from server.app import app
import os

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

def run_bot():
    api_id = 27893983
    api_hash = '7333605e802b401937e72688aeaa1ea3'
    phone = '+380979493781'
    source_channels = [-1001455546058, -1001594135954, -1001302199689, -1001498303038]
    target_chat = -1002129469860

    bot = TelegramVoiceBot(api_id, api_hash, phone, source_channels, target_chat)
    asyncio.run(bot.start())

if __name__ == '__main__':
    p1 = Process(target=run_flask)
    p2 = Process(target=run_bot)

    p1.start()
    p2.start()

    p1.join()
    p2.join()
