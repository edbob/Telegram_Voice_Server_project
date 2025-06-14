from flask import Flask, request, jsonify
import os
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_voice():
    voice = request.files.get('voice')
    text = request.form.get('text', '')

    if not voice:
        return jsonify({'error': 'Нет файла'}), 400

    # Сохраняем голосовой файл
    filename = datetime.now().strftime("%Y%m%d_%H%M%S") + '.mp3'
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    voice.save(save_path)

    print(f"Получен голосовой: {filename}")
    print(f"Текст: {text}")

    return jsonify({'status': 'ok', 'filename': filename})

if __name__ == '__main__':
    app.run(debug=True)
