from flask import Flask, request, render_template, jsonify, send_from_directory
import os
import shutil
from datetime import datetime
from flask import Response
from queue import Queue
import sqlite3

app = Flask(__name__, static_folder='static', template_folder='templates')

UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
VOICE_FOLDER = os.path.join(app.root_path, 'static', 'voice')

# Убедимся, что нужные папки существуют
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VOICE_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/messages')
def get_messages():
    files = os.listdir(VOICE_FOLDER)
    files = [f for f in files if f.endswith('.ogg')]

    # Сортировка файлов по дате создания — последние сверху
    files = sorted(files, key=lambda f: os.path.getctime(os.path.join(VOICE_FOLDER, f)), reverse=True)

    latest_files = files[:10]

    # Подключаемся к базе
    DB_PATH = os.path.join(app.root_path, '..', 'bot', 'messages.db')
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Получаем последние 10 сообщений из базы (source, date)
    c.execute('''
        SELECT date, source FROM messages ORDER BY date DESC LIMIT 10
    ''')
    rows = c.fetchall()
    conn.close()

    messages = []

    for i, f in enumerate(latest_files):
        path = os.path.join(VOICE_FOLDER, f)
        created = datetime.fromtimestamp(os.path.getctime(path)).strftime('%Y-%m-%d %H:%M:%S')

        # Попробуем взять соответствующий source
        if i < len(rows):
            source = rows[i][1]
        else:
            source = "Неизвестно"

        messages.append({
            'filename': f,
            'url': f'/static/voice/{f}',
            'date': created,
            'source': source
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

    # Копируем в static/voice/
    static_path = os.path.join(VOICE_FOLDER, file.filename)
    shutil.copy(save_path, static_path)

    print(f"✅ Загружено: {save_path}")
    print(f"📁 Скопировано в: {static_path}")
    notify_clients()
    return 'Файл получен', 200

def init_db():
    import sqlite3
    db_path = os.path.join(os.path.dirname(__file__), 'messages.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            date TEXT NOT NULL,
            source TEXT
        )
    ''')

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
