import pyaudio
from google.cloud import speech
from PyQt6.QtCore import QThread, pyqtSignal, pyqtSlot


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
            # Hangfelvétel beállítása
            RATE = 16000
            CHUNK = int(RATE / 10)  # 100ms

            audio = pyaudio.PyAudio()
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
            )

            # Google Speech kliens
            client = speech.SpeechClient()

            # Streaming felismerés konfigurálása
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=RATE,
                language_code=self.language_code,
                enable_automatic_punctuation=True,
            )
            streaming_config = speech.StreamingRecognitionConfig(config=config, interim_results=True)

            # Streaming felismerés indítása - alternatív megoldás
            def audio_generator():
                # Először a konfiguráció kérést küldjük el
                yield speech.StreamingRecognizeRequest(streaming_config=streaming_config)

                # Majd az audio adatokat
                while self.running:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    yield speech.StreamingRecognizeRequest(audio_content=data)

            # Létrehozzuk a generátort
            audio_requests = audio_generator()

            # Meghívjuk a streaming_recognize metódust a generátorral
            responses = client.streaming_recognize(audio_requests)

            # Feldolgozzuk a válaszokat
            for response in responses:
                if not self.running:
                    break

                if not response.results:
                    continue

                result = response.results[0]

                if result.is_final:
                    transcript = result.alternatives[0].transcript
                    self.textReady.emit(transcript)

        except Exception as e:
            self.error.emit(str(e))
        finally:
            if "stream" in locals():
                stream.stop_stream()
                stream.close()
            if "audio" in locals():
                audio.terminate()

            self.running = False

    def stop(self):
        """Beszédfelismerés leállítása"""
        self.running = False
