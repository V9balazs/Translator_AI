import os

import pyaudio
from google.cloud import speech
from PyQt6.QtCore import QThread, pyqtSignal, pyqtSlot

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"


class SpeechRecognitionThread(QThread):
    textReady = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, language_code="hu-HU"):
        super().__init__()
        self.language_code = language_code
        self.running = False

    def run(self):
        """Beszédfelismerés futtatása"""
        self.running = True

        try:
            # Audió konfigurálása - közvetlenül a speech_test.py-ból
            RATE = 16000
            CHUNK = int(RATE / 10)  # 100ms
            FORMAT = pyaudio.paInt16
            CHANNELS = 1

            # Speech kliens inicializálása - közvetlenül a speech_test.py-ból
            client = speech.SpeechClient()
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=RATE,
                language_code=self.language_code,  # Itt használjuk az osztály language_code attribútumát
                enable_automatic_punctuation=True,
            )

            streaming_config = speech.StreamingRecognitionConfig(
                config=config,
                interim_results=True,
            )

            # Mikrofon stream inicializálása - közvetlenül a speech_test.py-ból
            p = pyaudio.PyAudio()
            stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
            )

            # Streaming felismerés - közvetlenül a speech_test.py-ból, de módosítva
            def generate_requests():
                while self.running:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    yield speech.StreamingRecognizeRequest(audio_content=data)

            responses = client.streaming_recognize(streaming_config, generate_requests())

            # Válaszok feldolgozása - közvetlenül a speech_test.py-ból, de módosítva
            for response in responses:
                if not self.running:  # Kilépünk, ha a szál leállítását kérték
                    break

                if not response.results:
                    continue

                result = response.results[0]
                if not result.alternatives:
                    continue

                transcript = result.alternatives[0].transcript

                if result.is_final:
                    # Végleges eredmény esetén jelezzük a felhasználói felületnek
                    self.textReady.emit(transcript)

        except Exception as e:
            self.error.emit(str(e))
        finally:
            if "stream" in locals():
                stream.stop_stream()
                stream.close()
            if "p" in locals():
                p.terminate()

            self.running = False

    def stop(self):
        """Beszédfelismerés leállítása"""
        self.running = False
