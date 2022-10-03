from threading import Thread
import numpy as np
import queue
import sounddevice as sd
from scipy.fftpack import fft
from core.events import ThreadEmitter

CHANNELS = 1
INPUT_DEVICE = None  # 4
MAIN_STREAM_SAMPLE_RATE = 44100
MAIN_STREAM_BLOCK_SIZE = 8000

audio_chunk_callbacks = {}


def TransformAudioChunks(audio_chunk,out_sample_rate=MAIN_STREAM_SAMPLE_RATE,out_blocksize=MAIN_STREAM_BLOCK_SIZE, in_sample_rate=MAIN_STREAM_SAMPLE_RATE, in_blocksize=MAIN_STREAM_BLOCK_SIZE):
    return audio_chunk


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
        self.audio_buffer.put(TransformAudioChunks(in_data,out_blocksize=self.chunk))

    def run(self):
        audio_chunk_callbacks[self.id] = self.OnStreamChunkReceived
        while True:
            if self.callback and callable(self.callback):
                audio_chunk = self.audio_buffer.get()
                if self.is_fft:
                    if audio_chunk:
                        decoded = np.frombuffer(audio_chunk, dtype=np.int16)
                        chunk = np.frombuffer(audio_chunk, dtype=np.int16)
                        m = len(decoded) // self.chunk
                        decoded = chunk.reshape(-1, m).mean(axis=1)
                        fft_decode = fft(decoded) / (len(decoded) / 2)  # normalized FFT
                        mags = np.absolute(fft(decoded))  #
                        new_arr = [0 for element in range(len(mags))]
                        max = len(mags)
                        diff = len(mags) // 2
                        #for x in range(len(new_arr)):
                            #new_arr[(x + diff) % max] = mags[x]
                        self.callback(mags)
                else:
                    if audio_chunk:
                        self.callback(audio_chunk)

                # self.ProcessJobs()


def StartVoice(callback, chunk=1024, samplerate_in=44100, samplerate_out=44100, is_fft=True):
    voice = VoiceThread(callback, chunk, samplerate_in, samplerate_out, is_fft)
    voice.start()
    return voice


def OnAudioChunk(in_data, frame_count, time_info, flag):
    for callback in audio_chunk_callbacks.values():
        callback(in_data, frame_count, time_info, flag)


def StartStream():
    with sd.RawInputStream(samplerate=MAIN_STREAM_SAMPLE_RATE, blocksize=MAIN_STREAM_BLOCK_SIZE, device=INPUT_DEVICE,
                           dtype="int16", channels=1, callback=OnAudioChunk):
        while True:
            sd.sleep(9000000)


sound_thread = Thread(daemon=True, target=StartStream, group=None)
sound_thread.start()
