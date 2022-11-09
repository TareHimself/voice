from threading import Thread
import numpy as np
import queue
import pyaudio
import sounddevice as sd

from core.events import ThreadEmitter

CHANNELS = 1
DEFAULT_INPUT_DEVICE = None  # 4
DEFAULT_SAMPLE_RATE = 16000
MAIN_STREAM_BLOCK_SIZE = 8000
FORMAT = pyaudio.paInt16


class VoiceThread(ThreadEmitter):

    def __init__(self, callback, chunk=None, device=DEFAULT_INPUT_DEVICE, samplerate=DEFAULT_SAMPLE_RATE):
        super(VoiceThread, self).__init__()
        self.chunk = chunk
        self.samplerate = samplerate
        self.callback = callback
        self.device = None

    def run(self):
        while True:
            audio = pyaudio.PyAudio()

            # A frame must be either 10, 20, or 30 ms in duration for webrtcvad
            FRAME_DURATION = 30
            CHUNK = self.chunk if self.chunk else int(
                self.samplerate * FRAME_DURATION / 1000)

            stream = audio.open(input_device_index=self.device,
                                format=FORMAT,
                                channels=CHANNELS,
                                rate=self.samplerate,
                                input=True,
                                frames_per_buffer=CHUNK)

            while True:
                if self.callback and callable(self.callback):
                    audio_chunk = stream.read(
                        CHUNK, exception_on_overflow=False)
                    if audio_chunk:
                        self.callback(audio_chunk)

                # self.ProcessJobs()


def StartVoice(callback, chunk=None, device=DEFAULT_INPUT_DEVICE, samplerate=DEFAULT_SAMPLE_RATE):
    voice = VoiceThread(callback, chunk, device, samplerate)
    voice.start()
    return voice
