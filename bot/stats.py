from datetime import datetime, timedelta
import matplotlib.pyplot as plt

class StatsProcessor:
    def __init__(self, db):
        """
        db — это объект MessageDB
        """
        self.db = db

        # Стемы (ловят варианты: тревога/тревожная, тривога/повітряна, "воздушка" и т.п.)
        self.alert_stems = ["тревог", "тривог", "повiтр", "повітр", "воздуш", "🚨"]
        self.clear_stems = ["отбой", "відбій", "відбiй", "скасув", "all clear", "відміна"]

        # Фразы, которые НЕ считаем реальным "отбоем"
        self.clear_blacklist = [
            "ожидаем отбой", "ждём отбой", "ждем отбой", "ожидаем", "ожидаем отмену"
        ]

    @staticmethod
    def _parse_dt(s: str):
        if not s:
            return None
        s = s.strip()
        # ISO: 2025-07-24T14:30:01+00:00 или ...Z
        if "T" in s:
            try:
                return datetime.fromisoformat(s.replace("Z", "+00:00")).replace(tzinfo=None)
            except Exception:
                pass
        # DD.MM.YYYY HH:MM[:SS]
        for fmt in ("%d.%m.%Y %H:%M:%S", "%d.%m.%Y %H:%M"):
            try:
                return datetime.strptime(s, fmt)
            except Exception:
                continue
        return None

    def _is_alert_like(self, text: str) -> bool:
        t = (text or "").lower()
        return any(st in t for st in self.alert_stems)

    def _is_clear_like(self, text: str) -> bool:
        t = (text or "").lower()
        if any(bad in t for bad in self.clear_blacklist):
            return False
        return any(st in t for st in self.clear_stems)

    def _load_messages_period(self, days: int):
        """
        Берём все сообщения из БД, парсим даты в Python,
        фильтруем по окну now-<days>..now.
        """
        now = datetime.now()
        start = now - timedelta(days=days)
        rows = self.db.get_all_messages()

        parsed = []
        for _id, msg, date_str in rows:
            ts = self._parse_dt(date_str)
            if ts is None:
                continue
            if start <= ts <= now:
                parsed.append((_id, ts, msg or ""))

        parsed.sort(key=lambda x: x[1])  # по времени
        return parsed, start, now

    def get_air_alert_stats(self, period='day'):
        if period == 'day':
            days = 1
        elif period == 'week':
            days = 7
        elif period == 'month':
            days = 30
        else:
            raise ValueError("Unsupported period")

        rows, start_dt, now = self._load_messages_period(days)

        intervals = []
        alert_start = None

        for _id, ts, text in rows:
            if alert_start is None and self._is_alert_like(text):
                alert_start = ts
                continue
            if alert_start is not None and self._is_clear_like(text):
                duration = (ts - alert_start).total_seconds() / 60.0
                if 0 < duration < 12 * 60:  # отсечём аномалии > 12ч
                    intervals.append((alert_start, ts, duration))
                alert_start = None

        # Если тревога ещё не завершилась
        if alert_start is not None:
            duration = (now - alert_start).total_seconds() / 60.0
            intervals.append((alert_start, now, duration))

        total_alerts = len(intervals)
        total_minutes = round(sum(d for _, _, d in intervals))
        avg_minutes = round(total_minutes / total_alerts) if total_alerts else 0

        return {
            'count': total_alerts,
            'total_minutes': total_minutes,
            'avg_minutes': avg_minutes,
            'last_alert': intervals[-1][0].strftime('%H:%M %d.%m.%Y') if intervals else '—',
            'last_clear': intervals[-1][1].strftime('%H:%M %d.%m.%Y') if intervals else '—',
            'intervals': [
                {
                    'start': a.strftime('%Y-%m-%d %H:%M'),
                    'end': b.strftime('%Y-%m-%d %H:%M'),
                    'minutes': round(d)
                } for a, b, d in intervals
            ]
        }

    def get_alerts_per_day(self, days=7):
        """
        Считает количество тревог по каждому дню за последние N дней.
        """
        rows, start, now = self._load_messages_period(days)
        counts = {}

        for _id, ts, text in rows:
            if self._is_alert_like(text):
                d = ts.strftime("%Y-%m-%d")
                counts[d] = counts.get(d, 0) + 1

        return counts

def plot_alerts_per_day(alerts: dict, filename="stats.png"):
    if not alerts:
        return None  # нечего рисовать

    dates = list(alerts.keys())
    values = list(alerts.values())

    plt.figure(figsize=(8,4))
    plt.bar(dates, values, color="red")
    plt.xticks(rotation=45, ha="right")
    plt.title("Количество тревог по дням")
    plt.xlabel("Дата")
    plt.ylabel("Количество тревог")
    plt.tight_layout()

    plt.savefig(filename)
    plt.close()
    return filename