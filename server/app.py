from flask import Flask, request, render_template, jsonify, send_from_directory
import os
import shutil
from datetime import datetime
from flask import Response
from queue import Queue
from bot.db import MessageDB

app = Flask(__name__, static_folder='static', template_folder='templates')

UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
VOICE_FOLDER = os.path.join(app.root_path, 'static', 'voice')

# Убедимся, что нужные папки существуют
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VOICE_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

db = MessageDB()

@app.route('/api/messages')
def get_messages():
    messages = db.get_latest_messages()
    for msg in messages:
        msg['url'] = msg['filename']
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

    # Копируем в static/voice/
    static_path = os.path.join(VOICE_FOLDER, file.filename)
    shutil.copy(save_path, static_path)
    
    # Временные данные (в реальности бот должен передавать это через POST вместе с файлом)
    sender_id = 0
    message = '---'
    date = datetime.now().isoformat()
    source = 'Неизвестно'
    filename = file.filename

    db.save_message(sender_id, message, date, source, filename)


    print(f"✅ Загружено: {save_path}")
    print(f"📁 Скопировано в: {static_path}")
    notify_clients()
    return 'Файл получен', 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)