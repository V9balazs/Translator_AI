import os

from PyQt6 import uic
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QMainWindow, QMessageBox

from speech_recognision_thread import SpeechRecognitionThread


class TranslatorWindow(QMainWindow):
    # A főablak inicializálása
    def __init__(self, translator):
        super().__init__()
        self.translator = translator

        ui_file = os.path.join(os.path.dirname(__file__), "main_window.ui")
        uic.loadUi(ui_file, self)

        self.languages = self.translator.get_language()
        self.setup_language_combos()

        self.speech_thread = None
        self.setup_speech_recognition()

        self.connect_signals()

    # Legördülő menübe nyelvek beállítása
    def setup_language_combos(self):
        self.Source_Language.clear()
        self.Target_Language.clear()

        self.Source_Language.addItem("Automatic")

        for code, name in self.languages.items():
            self.Source_Language.addItem(name, code)
            self.Target_Language.addItem(name, code)

    # Beszédfelismerés beállítása
    def setup_speech_recognition(self):
        if hasattr(self, "Speech_To_Text_Button"):
            self.Speech_To_Text_Button.setChecked(False)
            self.Speech_To_Text_Button.clicked.connect(self.toggle_speech_recognition)

    # Kattintás események összekapcsolása
    def connect_signals(self):
        self.Translate_Button.clicked.connect(self.translate_text)

    @pyqtSlot(bool)
    def toggle_speech_recognition(self, checked):
        if checked:
            try:
                # Nyelv kód lekérése
                source_lang = self.Source_Language.currentData()
                if not source_lang:
                    source_lang = "en-US"
                else:
                    # Átalakítás Google Speech formátumra
                    lang_mapping = {
                        "en": "en-US",
                        "hu": "hu-HU",
                        "de": "de-DE",
                        "fr": "fr-FR",
                        "es": "es-ES",
                        "it": "it-IT",
                        "ja": "ja-JP",
                        "ko": "ko-KR",
                        "pt": "pt-BR",
                        "ru": "ru-RU",
                        "zh": "zh-CN",
                    }
                    source_lang = lang_mapping.get(source_lang, f"{source_lang}-{source_lang.upper()}")

                # Beszédfelismerés szál létrehozása
                self.speech_thread = SpeechRecognitionThread(language_code=source_lang)
                self.speech_thread.textReady.connect(self.on_speech_recognized)
                self.speech_thread.error.connect(self.on_speech_error)
                self.speech_thread.start()

                self.Speech_To_Text_Button.setText("Speech to text ON")

            except ImportError as e:
                QMessageBox.warning(
                    self,
                    "Hiányzó modulok",
                    f"A beszédfelismeréshez szükséges modulok hiányoznak: {str(e)}\n\n"
                    "Telepítsd a következő csomagokat:\npip install pyaudio google-cloud-speech",
                )
                self.Speech_To_Text_Button.setChecked(False)
            except Exception as e:
                QMessageBox.warning(self, "Hiba", f"Hiba történt a beszédfelismerés indításakor: {str(e)}")
                self.Speech_To_Text_Button.setChecked(False)
        else:
            # Beszédfelismerés kikapcsolása
            self.Speech_To_Text_Button.setText("Speech to text OFF")

            if self.speech_thread and self.speech_thread.running:
                self.speech_thread.stop()
                self.speech_thread = None

    # Fordítás folyamat kezdeményezése
    @pyqtSlot()
    def translate_text(self):
        source_text = self.Source_Text.toPlainText()

        source_lang = self.Source_Language.currentData()
        if source_lang == "auto" or source_lang == "Automatic" or not source_lang:
            source_lang = None

        target_lang = self.Target_Language.currentData()

        if not source_text:
            return

        try:
            # Fordítás végrehajtása
            result = self.translator.translate_text(
                source_text, target_language=target_lang, source_language=source_lang
            )

            # Eredmény megjelenítése
            self.Target_Text.setPlainText(result["translated_text"])

            # Ha automatikus felismerés volt, frissítsük a forrás nyelvet
            if not source_lang and result["detected_language"]:
                detected = result["detected_language"]
                index = self.Source_Language.findData(detected)
                if index > 0:  # 0 az "Automatikus felismerés"
                    self.Source_Language.setCurrentIndex(index)

        except Exception as e:
            self.Target_Text.setPlainText(f"Hiba történt: {str(e)}")
            print(f"Fordítási hiba: {str(e)}")

    @pyqtSlot(str)
    def on_speech_recognized(self, text):
        """Beszédfelismerés eredményének kezelése"""
        current_text = self.Source_Text.toPlainText()

        # Ha már van szöveg, új sorba írjuk
        if current_text and not current_text.endswith("\n"):
            self.Source_Text.setPlainText(f"{current_text}\n{text}")
        else:
            self.Source_Text.setPlainText(f"{current_text}{text}")

        # Opcionális: automatikus fordítás
        self.translate_text()

    @pyqtSlot(str)
    def on_speech_error(self, error_message):
        """Beszédfelismerés hibájának kezelése"""
        QMessageBox.warning(self, "Beszédfelismerési hiba", f"Hiba történt a beszédfelismerés során: {error_message}")

        # Kikapcsoljuk a beszédfelismerést
        self.Speech_To_Text_Button.setChecked(False)
        self.toggle_speech_recognition(False)
