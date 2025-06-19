# bot/db.py — версия с PostgreSQL
import psycopg2
import os

class MessageDB:
    def __init__(self):
        self.conn = psycopg2.connect(os.environ['DATABASE_URL'])
        self.create_table()

    def create_table(self):
        with self.conn.cursor() as c:
            c.execute('DROP TABLE IF EXISTS messages')
            c.execute('''
                CREATE TABLE messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender_id INTEGER,
                    message TEXT,
                    date TEXT,
                    source TEXT,
                    filename TEXT
                )
            ''')
            self.conn.commit()

    def save_message(self, sender_id, message, date, source, filename):
        with self.conn.cursor() as c:
            c.execute('''
                INSERT INTO messages (sender_id, message, date, source, filename)
                VALUES (%s, %s, %s, %s, %s)
            ''', (sender_id, message, date, source, filename))
            self.conn.commit()

    def get_latest_messages(self, limit=10):
        with self.conn.cursor() as c:
            c.execute('''
                SELECT filename, date, source
                FROM messages
                ORDER BY date DESC
                LIMIT %s
            ''', (limit,))
            rows = c.fetchall()
        return [
            {'filename': row[0], 'date': row[1].strftime('%Y-%m-%d %H:%M:%S'), 'source': row[2] or 'Неизвестно'}
            for row in rows
        ]