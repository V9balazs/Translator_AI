import os

from dotenv import load_dotenv
from google.cloud import translate_v2 as translate

load_dotenv()


class Translator:
    # Google Translate API inicializálása
    def __init__(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
        self.client = translate.Client()

    # Elérhető nyelvek lekérdezése
    def get_language(self):
        languages = self.client.get_languages()
        return {lang["language"]: lang["name"] for lang in languages}

    # Fordítás végrehajtás logikája
    def translate_text(self, text, target_language, source_language=None):
        if not text:
            return {"translated_text": "", "detected_language": None, "input_text": ""}

        # Ha a forrás nyelv üres string vagy "Automatic", állítsuk None-ra
        if source_language == "" or source_language == "Automatic":
            source_language = None

        try:
            result = self.client.translate(text, target_language=target_language, source_language=source_language)

            return {
                "translated_text": result["translatedText"],
                "detected_language": result.get("detectedSourceLanguage", source_language),
                "input_text": text,
            }
        except Exception as e:
            print(f"Fordítási hiba: {str(e)}")
            return {
                "translated_text": f"Hiba történt a fordítás során: {str(e)}",
                "detected_language": None,
                "input_text": text,
            }
