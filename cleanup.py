import os
import time
from datetime import datetime, timedelta

# Папки с аудио
FOLDERS = ['static/voice', 'uploads']

# Максимальный "возраст" файлов в секундах (24 часа)
MAX_AGE = 24 * 60 * 60  # 86400 секунд

def cleanup_old_files():
    now = time.time()

    for folder in FOLDERS:
        for filename in os.listdir(folder):
            path = os.path.join(folder, filename)
            if os.path.isfile(path):
                file_age = now - os.path.getctime(path)
                if file_age > MAX_AGE:
                    print(f"Удаляю {path}")
                    os.remove(path)

if __name__ == "__main__":
    cleanup_old_files()