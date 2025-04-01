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
            audio_format = pyaudio.paInt16
            channels = 1
            rate = 16000
            chunk = 1024

            audio = pyaudio.PyAudio()
            stream = audio.open(format=audio_format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)

            # Google Speech kliens
            client = speech.SpeechClient()

            # Streaming felismerés konfigurálása
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=rate,
                language_code=self.language_code,
                enable_automatic_punctuation=True,
            )
            streaming_config = speech.StreamingRecognitionConfig(config=config, interim_results=True)

            # Közvetlen megoldás: Külön létrehozzuk a konfiguráció kérést
            config_request = speech.StreamingRecognizeRequest(streaming_config=streaming_config)

            # Létrehozunk egy listát a kérésekhez
            requests = [config_request]

            # Adatgyűjtő függvény
            def audio_generator():
                while self.running:
                    data = stream.read(chunk, exception_on_overflow=False)
                    yield speech.StreamingRecognizeRequest(audio_content=data)

            # Streaming felismerés indítása a közvetlen megoldással
            # Először elküldjük a konfigurációt, majd az audio adatokat
            responses = client.streaming_recognize(requests + list(audio_generator()))

            # # Streaming felismerés indítása
            # def generate_requests():
            #     yield speech.StreamingRecognizeRequest(streaming_config=streaming_config)

            #     while self.running:
            #         data = stream.read(chunk, exception_on_overflow=False)
            #         yield speech.StreamingRecognizeRequest(audio_content=data)

            # requests_iterator = generate_requests()
            # responses = client.streaming_recognize(requests_iterator)

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
