import json
import os
import time
from io import BytesIO
from typing import Callable
import numpy as np
from core.events import global_emitter, ThreadEmitter
from .voice import StartVoice
from scipy.fftpack import fft


class FFTThread(ThreadEmitter):

    def __init__(self, callback=0, channels=64, samplerate=44100):
        super(FFTThread, self).__init__()
        self.samplerate = samplerate
        self.callback = callback
        self.channels = channels

    def OnVoiceChunk(self, d):
        if callable(self.callback):
            decoded = np.frombuffer(d, dtype=np.int16)
            mags = np.absolute(fft(decoded))  #
            new_arr = [0 for element in range(len(mags))]
            max = len(mags)
            diff = len(mags) // 2
            for x in range(len(new_arr)):
                new_arr[(x + diff) % max] = mags[x]
            self.callback(new_arr)

    def run(self):
        StartVoice(callback=self.OnVoiceChunk,
                   samplerate=self.samplerate, chunk=self.channels)
        while True:
            time.sleep(500000)


def StartFFT(callback=0, channels=64, samplerate=44100):
    fft = FFTThread(callback=callback, channels=channels, samplerate=44100)
    fft.start()
    return fft
