from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
DB_URL = os.getenv("DB_URL")
PHONE = os.getenv("PHONE")
API_HASH = os.getenv("API_HASH")
TARGET_CHAT = int(os.getenv("TARGET_CHAT", 0))
OpenWeatherMap_API_KEY = os.getenv("OpenWeatherMap_API_KEY")
UPLOAD_URL = os.getenv("UPLOAD_URL")