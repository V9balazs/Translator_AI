import os

from dotenv import load_dotenv
from google.cloud import translate_v2 as translate

load_dotenv()


class Translator:
    def __init__(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
        self.client = translate.Client()

    def get_language(self):
        languages = self.client.get_languages()
        return {lang["language"]: lang["name"] for lang in languages}

    def translate_text(self, text, target_language, source_language=None):
        if not text:
            return ""

        result = self.client.translate(text, target_language=target_language, source_language=source_language)

        return {
            "translated_text": result["translatedText"],
            "detected_language": result.get("detectedSourceLanguage", source_language),
            "input_text": text,
        }
