from threading import Thread
import numpy as np
import queue
import pyaudio
import sounddevice as sd

from core.events import ThreadEmitter

CHANNELS = 1
INPUT_DEVICE = None  # 4
MAIN_STREAM_SAMPLE_RATE = 44100
MAIN_STREAM_BLOCK_SIZE = 8000
FORMAT = pyaudio.paInt16


class VoiceThread(ThreadEmitter):

    def __init__(self, callback, chunk=None, samplerate_in=44100):
        super(VoiceThread, self).__init__()
        self.chunk = chunk
        self.samplerate_in = samplerate_in
        self.callback = callback

    def run(self):
        while True:
            audio = pyaudio.PyAudio()

            RATE = 16000
            # A frame must be either 10, 20, or 30 ms in duration for webrtcvad
            FRAME_DURATION = 30
            CHUNK = self.chunk if self.chunk else int(
                RATE * FRAME_DURATION / 1000)

            stream = audio.open(input_device_index=INPUT_DEVICE,
                                format=FORMAT,
                                channels=CHANNELS,
                                rate=self.samplerate_in,
                                input=True,
                                frames_per_buffer=CHUNK)

            while True:
                if self.callback and callable(self.callback):
                    audio_chunk = stream.read(
                        CHUNK, exception_on_overflow=False)
                    if audio_chunk:
                        self.callback(audio_chunk)

                # self.ProcessJobs()


def StartVoice(callback, chunk=None, samplerate=44100):
    voice = VoiceThread(callback, chunk, samplerate)
    voice.start()
    return voice
