# start_all.py
import subprocess
import time
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from multiprocessing import Process
from bot.telegram_bot import bot
from server.app import app

def run_bot():
    asyncio.run(bot.start())

def run_server():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    Process(target=run_bot).start()
    Process(target=run_server).start()