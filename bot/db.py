import sqlite3
from datetime import datetime, timedelta

class MessageDB:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
        self.init_db()
        self.delete_empty_messages()  # Удаление пустых сообщений
    
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

        try:
            c.execute("ALTER TABLE messages ADD COLUMN filename TEXT")
        except sqlite3.OperationalError:
            pass

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

    def get_messages_by_keywords(self, start_date, end_date, keywords):
        cursor = self.conn.cursor()
        query = f"""
            SELECT id, message, date FROM messages
            WHERE date BETWEEN ? AND ?
            AND ({' OR '.join(['message LIKE ?' for _ in keywords])})
            ORDER BY date ASC
        """
        params = [start_date, end_date] + [f"%{kw}%" for kw in keywords]
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return rows

    def get_air_alert_stats(self, period='day'):
        now = datetime.now()
        if period == 'day':
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'week':
            start = now - timedelta(days=7)
        elif period == 'month':
            start = now - timedelta(days=30)
        else:
            raise ValueError("Unsupported period")

        start_str = start.strftime('%Y-%m-%dT%H:%M:%S')  # ✅ формат ISO
        end_str = now.strftime('%Y-%m-%dT%H:%M:%S')

        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, message, date FROM messages
            WHERE date BETWEEN ? AND ?
            ORDER BY date ASC
        """, (start_str, end_str))

        rows = cursor.fetchall()

        alerts_keywords = ['тревога', 'повітряна', '🚨', 'воздушка']
        clears_keywords = ['отбой', 'відбій', 'відбій повітряної', 'скасування повітряної']

        result = []
        alert_start = None

        for msg_id, text, date_str in rows:
            text = text.lower()
            timestamp = datetime.fromisoformat(date_str.replace('Z', '+00:00'))

            if any(kw in text for kw in alerts_keywords) and not alert_start:
                alert_start = timestamp

            elif alert_start and any(kw in text for kw in clears_keywords):
                # Простая фильтрация фейковых отбоев
                if 'скоро' in text or 'будет' in text or 'если' in text or 'щас' in text:
                    continue
                duration = (timestamp - alert_start).total_seconds() / 60
                if duration > 0 and duration < 12 * 60:  # ограничим 12ч максимум
                    result.append((alert_start, timestamp, duration))
                alert_start = None

        # если тревога не закончилась
        if alert_start:
            duration = (now - alert_start).total_seconds() / 60
            result.append((alert_start, now, duration))

        total_alerts = len(result)
        total_duration = sum(d for _, _, d in result)
        avg_duration = total_duration / total_alerts if total_alerts else 0

        return {
            'count': total_alerts,
            'total_minutes': round(total_duration),
            'avg_minutes': round(avg_duration),
            'last_alert': result[-1][0].strftime('%H:%M %d.%m.%Y') if result else '—',
            'last_clear': result[-1][1].strftime('%H:%M %d.%m.%Y') if result else '—'
        }

    def close(self):
        if self.conn:
            self.conn.close()