import requests
from bot.config import OpenWeatherMap_API_KEY

API_KEY = OpenWeatherMap_API_KEY  # OpenWeatherMap API Key
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'

def get_weather(city='Odessa', lang='ru', units='metric'):
    try:
        params = {
            'q': city,
            'appid': API_KEY,
            'lang': lang,
            'units': units
        }
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        if response.status_code != 200 or 'weather' not in data:
            return "❌ Не удалось получить погоду."

        description = data['weather'][0]['description'].capitalize()
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        wind = data['wind']['speed']

        return (
            f"🌦️ Погода в {city}:\n"
            f"{description}\n"
            f"🌡️ Температура: {temp}°C (ощущается как {feels_like}°C)\n"
            f"💧 Влажность: {humidity}%\n"
            f"💨 Ветер: {wind} м/с"
        )
    except Exception as e:
        return f"⚠️ Ошибка при получении погоды: {e}"