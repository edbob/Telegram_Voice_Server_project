import sqlite3

class MessageDB:
    def __init__(self, db_file):
        self.db_file = db_file
        self.init_db()  

    def init_db(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER,
                message TEXT,
                date TEXT,
                source TEXT,
                filename TEXT
            )
        ''')

        # Пытаемся добавить колонку filename, если она ещё не существует (можно убрать, если уже есть)
        try:
            c.execute("ALTER TABLE messages ADD COLUMN filename TEXT")
        except sqlite3.OperationalError:
            pass

        conn.commit()
        conn.close()

    def save_message(self, sender_id, message, date, source, filename):
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO messages (sender_id, message, date, source, filename)
                VALUES (?, ?, ?, ?, ?)
            ''', (sender_id, message, date, source, filename))
            conn.commit()