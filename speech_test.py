import io
import os

import pyaudio
from google.cloud import speech

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"


def transcribe_microphone_stream():
    # Audió konfigurálása
    RATE = 16000
    CHUNK = int(RATE / 10)  # 100ms
    FORMAT = pyaudio.paInt16
    CHANNELS = 1

    # Speech kliens inicializálása
    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code="hu-HU",  # Módosíthatod a nyelvet igény szerint
        enable_automatic_punctuation=True,
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True,
    )

    # Mikrofon stream inicializálása
    p = pyaudio.PyAudio()
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
    )

    print("Beszélj a mikrofonba! A kilépéshez nyomd meg a Ctrl+C billentyűket.")

    # Streaming felismerés
    def generate_requests():
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            yield speech.StreamingRecognizeRequest(audio_content=data)

    responses = client.streaming_recognize(streaming_config, generate_requests())

    try:
        for response in responses:
            if not response.results:
                continue

            result = response.results[0]
            if not result.alternatives:
                continue

            transcript = result.alternatives[0].transcript

            if result.is_final:
                print(f"Felismert szöveg: {transcript}")
    except KeyboardInterrupt:
        print("Felismerés leállítva.")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()


if __name__ == "__main__":
    transcribe_microphone_stream()
