import emoji
import re
from langdetect import detect

class TextProcessor:
    @staticmethod
    def clean(input_string):
        text = emoji.replace_emoji(input_string, '')
        text = re.sub(r'[!@#$%^&*()_+=\[\]{};:"\\|,.<>/?~`]', '', text)
        text = re.sub(r'http\S+|www\.\S+', '', text)
        return text

    @staticmethod
    def detect_lang(text):
        try:
            lang = detect(text)
            return 'uk' if lang == 'uk' else 'ru'
        except Exception:
            return 'ru'