import os

from PyQt6 import uic
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QApplication, QMainWindow


class TranslatorWindow(QMainWindow):
    # A főablak inicializálása
    def __init__(self, translator):
        super().__init__()
        self.translator = translator
        ui_file = os.path.join(os.path.dirname(__file__), "main_window.ui")
        uic.loadUi(ui_file, self)
        self.languages = self.translator.get_language()
        self.setup_language_combos()
        self.connect_signals()

    # Legördülő menübe nyelvek beállítása
    def setup_language_combos(self):
        self.Source_Language.clear()
        self.Target_Language.clear()

        self.Source_Language.addItem("Automatic")

        for code, name in self.languages.items():
            self.Source_Language.addItem(name, code)
            self.Target_Language.addItem(name, code)

    # Kattintás események összekapcsolása
    def connect_signals(self):
        self.Translate_Button.clicked.connect(self.translate_text)

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
