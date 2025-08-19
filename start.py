import asyncio
import sys
import os
import socket
import traceback

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
processes = []

# Проверка подключения к интернету
def internet_available():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

async def run_process(name, path):
    while True:
        try:
            if not internet_available():
                print(f"⚠️ Нет подключения к интернету. Ждём...")
                await asyncio.sleep(5)
                continue

            print(f"🚀 Запуск {name}...")
            process = await asyncio.create_subprocess_exec(sys.executable, path)
            processes.append(process)

            returncode = await process.wait()
            print(f"🔄 {name} завершился с кодом {returncode}. Перезапуск через 2 сек...")
            await asyncio.sleep(2)

        except Exception as e:
            print(f"❌ Ошибка в {name}: {e}")
            traceback.print_exc()
            await asyncio.sleep(5)  # Подождать перед повтором

async def main():
    server_path = os.path.join(BASE_DIR, "server", "app.py")
    telegram_bot_path = os.path.join(BASE_DIR, "bot", "telegram_bot.py")
    menu_bot_path = os.path.join(BASE_DIR, "bot", "menu_bot.py")

    await asyncio.gather(
        run_process("Меню-бота", menu_bot_path),
        run_process("Flask сервера", server_path),
        run_process("Голосового бота", telegram_bot_path)
    )

def stop_all():
    print("\n⏹ Остановка всех процессов...")
    for proc in processes:
        if proc.returncode is None:
            try:
                proc.terminate()
            except ProcessLookupError:
                pass
    print("✅ Все процессы завершены.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        stop_all()
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        stop_all()