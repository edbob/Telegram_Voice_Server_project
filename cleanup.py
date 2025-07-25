import os
import time
from datetime import datetime, timedelta

# Получаем путь к текущей папке, где находится cleanup.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Папки, которые нужно очищать
FOLDERS = [
    os.path.join(BASE_DIR, 'server', 'static', 'voice'),
    os.path.join(BASE_DIR, 'server', 'uploads')
]

# Максимальный возраст файлов (в секундах): 7 дней = 604800
MAX_FILE_AGE = 7 * 24 * 60 * 60
print("Очистка запущена!")

def delete_old_files(folder):
    now = time.time()
    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)
        if os.path.isfile(path):
            file_age = now - os.path.getctime(path)
            print(f"Проверяю файл: {path}, возраст: {file_age} сек")
            if file_age > MAX_FILE_AGE:
                try:
                    os.remove(path)
                    print(f'Удален файл: {path}')
                except Exception as e:
                    print(f'Ошибка при удалении {path}: {e}')

def cleanup():
    for folder in FOLDERS:
        if os.path.exists(folder):
            delete_old_files(folder)
        else:
            print(f'Папка не найдена: {folder}')

with open("cleanup.log", "a", encoding="utf-8") as f:
    f.write(f"[{time.ctime()}] Очистка выполнена\n")

if __name__ == '__main__':
    cleanup()