import sys

from PyQt6.QtWidgets import QApplication

from translator import Translator
from ui.translator_window import TranslatorWindow


def main():
    app = QApplication(sys.argv)
    translator = Translator()
    window = TranslatorWindow(translator)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
