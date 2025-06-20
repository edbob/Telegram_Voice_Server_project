import cloudinary
import cloudinary.uploader
import os

# Конфигурация через переменные среды
cloudinary.config(
    cloud_name=os.environ['CLOUDINARY_CLOUD_NAME'],
    api_key=os.environ['CLOUDINARY_API_KEY'],
    api_secret=os.environ['CLOUDINARY_API_SECRET']
)

def upload_audio_to_cloudinary(file_path):
    try:
        result = cloudinary.uploader.upload(
            file_path,
            resource_type="video",  # audio/mp3/ogg = video по типу
            folder="telegram_voice",
            use_filename=True,
            unique_filename=False
        )
        return result['secure_url']
    except Exception as e:
        print("Ошибка загрузки в Cloudinary:", e)
        return None