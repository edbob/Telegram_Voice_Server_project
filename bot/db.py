import sqlite3

class MessageDB:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
        self.init_db()
        self.delete_empty_messages()

    def delete_empty_messages(self):
        c = self.conn.cursor()
        c.execute("DELETE FROM messages WHERE message IS NULL OR TRIM(message) = '';")
        self.conn.commit()

    def init_db(self):
        c = self.conn.cursor()
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
        c.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                user_id INTEGER,
                action TEXT,
                date TEXT
            )
        ''')
        self.conn.commit()

    def save_message(self, sender_id, message, date, source, filename):
        c = self.conn.cursor()
        c.execute('''
            INSERT INTO messages (sender_id, message, date, source, filename)
            VALUES (?, ?, ?, ?, ?)
        ''', (sender_id, message, date, source, filename))
        self.conn.commit()

    def save_stat(self, chat_id, user_id, action):
        c = self.conn.cursor()
        c.execute('''
            INSERT INTO stats (chat_id, user_id, action, date)
            VALUES (?, ?, ?, datetime('now'))
        ''', (chat_id, user_id, action))
        self.conn.commit()

    def get_messages_between(self, start_date, end_date):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, message, date FROM messages
            WHERE date BETWEEN ? AND ?
            ORDER BY date ASC
        """, (start_date, end_date))
        return cursor.fetchall()

    def close(self):
        if self.conn:
            self.conn.close()