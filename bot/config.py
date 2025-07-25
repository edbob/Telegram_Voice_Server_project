from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
DB_URL = os.getenv("DB_URL")
OpenWeatherMap_API_KEY = os.getenv("OpenWeatherMap_API_KEY")