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
                date TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def save_message(self, sender_id, text, date):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('INSERT INTO messages (sender_id, message, date) VALUES (?, ?, ?)',
                  (sender_id, text, date))
        conn.commit()
        conn.close()