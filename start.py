import asyncio
import sys
import os
import signal

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Храним процессы, чтобы можно было их остановить
processes = []

async def run_process(name, path):
    print(f"🚀 Запуск {name}...")
    process = await asyncio.create_subprocess_exec(sys.executable, path)
    processes.append(process)
    await process.wait()

async def main():
    server_path = os.path.join(BASE_DIR, "server", "app.py")
    telegram_bot_path = os.path.join(BASE_DIR, "bot", "telegram_bot.py")
    menu_bot_path = os.path.join(BASE_DIR, "bot", "menu_bot.py")

    await asyncio.gather(
        run_process("Flask сервера", server_path),
        run_process("Голосового бота", telegram_bot_path),
        run_process("Меню-бота", menu_bot_path),
    )

def stop_all():
    print("\n⏹ Остановка всех процессов...")
    for proc in processes:
        if proc.returncode is None:  # процесс ещё работает
            try:
                proc.terminate()  # мягкая остановка
            except ProcessLookupError:
                pass
    print("✅ Все процессы завершены.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        stop_all()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        stop_all()