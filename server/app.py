from flask import Flask, request, render_template, jsonify, send_from_directory
import os
import sys
import shutil
from datetime import datetime
from flask import Response
from queue import Queue
import sqlite3
import io
import threading
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from cleanup import cleanup
from bot.processor import TextProcessor

app = Flask(__name__, static_folder='static', template_folder='templates')

UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')

# Убедимся, что нужные папки существуют
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def background_cleanup():
    while True:
        print("🧹 Автоочистка старых файлов...")
        cleanup()
        time.sleep(24 * 60 * 60)  # раз в сутки

@app.route('/manifest.json')
def manifest():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'manifest.json')

@app.route('/sw.js')
def sw():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'sw.js')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/server/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.join(app.root_path, 'uploads'), filename)

@app.route('/api/messages')
def get_messages():
    DB_PATH = os.path.join(app.root_path, '..', 'bot', 'messages.db')
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    try:
        c.execute('''
            SELECT id, filename, message, date, source 
            FROM messages 
            ORDER BY id DESC 
            LIMIT 10
        ''')
        rows = c.fetchall()
    finally:
        conn.close()

    messages = []
    for row in rows:
        filename = row['filename']
        file_path = None
        need_update_db = False

        # если в базе нет имени файла → создаём новое
        if not filename:
            filename = f"voice_{row['id']}.mp3"
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            need_update_db = True
        else:
            file_path = os.path.join(UPLOAD_FOLDER, filename)

        # если файл не существует → озвучиваем
        if not os.path.exists(file_path):
            print(f"⚠️ Файл не найден: {filename}. Озвучиваем сообщение заново.")
            try:
                from gtts import gTTS
                text = row['message'] or ''
                tts = gTTS(text, lang='ru')
                tts.save(file_path)
                print(f"✅ Файл озвучен и сохранён: {file_path}")
                need_update_db = True
            except Exception as e:
                print(f"❌ Ошибка озвучивания: {e}")

        # если создали новый файл — обновим базу
        if need_update_db:
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.execute("UPDATE messages SET filename = ? WHERE id = ?", (filename, row['id']))
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"❌ Ошибка обновления базы: {e}")

        # Используем дату только из базы!
        created = row['date'] or 'Неизвестно'

        try:
            full_message = TextProcessor.clean(row['message'] or '')
        except Exception as e:
            print(f"❌ Ошибка обработки текста: {e}")
            full_message = row['message'] or ''

        preview = (full_message[:50] + '…') if len(full_message) > 50 else full_message

        messages.append({
            'id': row['id'],
            'filename': filename if os.path.exists(file_path) else None,
            'url': f'/server/uploads/{filename}' if os.path.exists(file_path) else None,
            'date': created,
            'source': row['source'] or "Неизвестно",
            'preview': preview,
            'full_message': full_message,
            'has_audio': os.path.exists(file_path)
        })

    return jsonify(messages)

subscribers = []

@app.route('/events')
def sse():
    def event_stream(q):
        while True:
            data = q.get()
            yield f"data: {data}\n\n"

    q = Queue()
    subscribers.append(q)
    return Response(event_stream(q), mimetype="text/event-stream")

def notify_clients():
    for q in subscribers:
        q.put('new_message')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'Нет файла!', 400

    file = request.files['file']
    if file.filename == '':
        return 'Пустое имя файла', 400

    # Сохраняем сначала в uploads/
    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(save_path)

    print(f"✅ Загружено: {save_path}")
    notify_clients()
    return 'Файл получен', 200

if __name__ == "__main__":
    threading.Thread(target=background_cleanup, daemon=True).start()
    app.run(debug=True)