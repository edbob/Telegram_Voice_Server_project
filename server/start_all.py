# start_all.py
import subprocess
import time

# Запускаем telegram-бота в фоне
print("Запуск telegram_bot.py...")
bot_proc = subprocess.Popen(["python3", "bot/telegram_bot.py"])

# Подождём 3-5 секунд, чтобы бот успел подключиться
time.sleep(5)

# Запускаем Flask-приложение
print("Запуск Flask app.py...")
subprocess.call(["python3", "server/app.py"])