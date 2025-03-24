import os

from PyQt6 import uic
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QApplication, QMainWindow


class TranslatorWindow(QMainWindow):
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
        self.Source_Language.addItem("Automatic")

        for code, name in self.languages.items():
            self.Source_Language.addItem(name)
            self.Target_Language.addItem(name)

        en_index = self.Source_Language.findData("en")
        if en_index >= 0:
            self.Source_Language.setCurrentIndex(en_index)

    def connect_signals(self):
        self.Translate_Button.clicked.connect(self.translate_text)

    @pyqtSlot()
    def translate_text(self):
        source_text = self.Source_Text.toPlainText()
        source_lang = self.Source_Language.currentText()
        target_lang = self.Target_Language.currentText()

        if not source_text:
            return

        result = self.translator.translate_text(source_text, target_lang, source_lang)

        self.Target_text.setPlainText(result["translated_text"])

        if not source_lang and result["detected_language"]:
            detected = result["detected_language"]
            index = self.Source_Language.findData(detected)
            if index >= 0:
                self.Target_Language.setCurrentIndex(index)
