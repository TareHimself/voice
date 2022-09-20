from threading import Thread
import numpy as np
import queue
import sounddevice as sd
from scipy.fftpack import fft

from events.thread_emitter import ThreadEmitter

CHANNELS = 1
INPUT_DEVICE = None#4


class VoiceThread(ThreadEmitter):

    def __init__(self, callback, chunk=1024, samplerate_in=44100, samplerate_out=44100, is_fft=True):
        super(VoiceThread, self).__init__()
        self.chunk = chunk
        self.samplerate_in = samplerate_in
        self.samplerate_out = samplerate_out
        self.audio_buffer = queue.Queue()
        self.is_fft = is_fft
        self.callback = callback

    def OnStreamChunkReceived(self, in_data, frame_count, time_info, flag):
        self.audio_buffer.put(in_data)

    def run(self):

        with sd.RawInputStream(samplerate=self.samplerate_in, blocksize=self.chunk, device=INPUT_DEVICE,
                               dtype="int16", channels=1, callback=self.OnStreamChunkReceived):
            while True:
                if self.callback and callable(self.callback):
                    audio_chunk = self.audio_buffer.get()
                    if self.is_fft:
                        if audio_chunk:
                            decoded = np.fromstring(audio_chunk, dtype=np.int16)
                            fft_decode = fft(decoded) / (len(decoded) / 2)  # normalized FFT
                            mags = np.absolute(fft(decoded))  #
                            new_arr = [0 for element in range(len(mags))]
                            max = len(mags)
                            diff = len(mags) // 2
                            for x in range(len(new_arr)):
                                new_arr[(x + diff) % max] = mags[x]
                            self.callback(new_arr)
                    else:
                        if audio_chunk:
                            self.callback(audio_chunk)

                #self.ProcessJobs()


def StartVoice(callback, chunk=1024, samplerate_in=44100, samplerate_out=44100, is_fft=True):
    voice = VoiceThread(callback, chunk, samplerate_in, samplerate_out, is_fft)
    voice.start()
    return voice
