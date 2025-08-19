from datetime import datetime, timedelta

class StatsProcessor:
    def __init__(self, db):
        """
        db — это объект MessageDB
        """
        self.db = db

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

        start_str = start.strftime('%Y-%m-%dT%H:%M:%S')
        end_str = now.strftime('%Y-%m-%dT%H:%M:%S')

        rows = self.db.get_messages_between(start_str, end_str)

        alerts_keywords = ['тревога', 'повітряна', '🚨', 'воздушка']
        clears_keywords = ['отбой', 'відбій', 'відбій повітряної', 'скасування повітряної']

        result = []
        alert_start = None

        for msg_id, text, date_str in rows:
            if not text:
                continue

            text = text.lower()
            timestamp = datetime.fromisoformat(date_str.replace('Z', '+00:00'))

            if any(kw in text for kw in alerts_keywords) and not alert_start:
                alert_start = timestamp

            elif alert_start and any(kw in text for kw in clears_keywords):
                if any(x in text for x in ['скоро', 'будет', 'если', 'щас']):
                    continue
                duration = (timestamp - alert_start).total_seconds() / 60
                if 0 < duration < 12 * 60:
                    result.append((alert_start, timestamp, duration))
                alert_start = None

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