import json
import os
from threading import Thread
from typing import Callable

import requests
from vosk import Model, KaldiRecognizer, SetLogLevel
from os import getcwd, path, mkdir, listdir
from events.thread_emitter import ThreadEmitter
from threads.voice import StartVoice
from io import BytesIO
from zipfile import ZipFile
import time
from urllib.request import urlopen

SetLogLevel(-1)

model_downloaded = False
model_downloading = False


def DownloadFile(url: str, OnProgress: Callable[[int, int], None] = lambda t, p: None):
    f = BytesIO()
    r = requests.get(url, stream=True)
    total = r.headers["Content-Length"]

    for chunk in r.iter_content(1024):
        f.write(chunk)
        OnProgress(total, f.getbuffer().nbytes)

    return f


class SpeechRecognitionThread(ThreadEmitter):

    def __init__(self, callback=0, onStart=0, samplerate_in=44100):
        super(SpeechRecognitionThread, self).__init__()
        self.samplerate_in = samplerate_in
        self.callback = callback
        self.onStart = onStart
        self.mic = None
        self.model = None
        self.rec = None
        self.bShouldProcessData = True

    def OnVoiceChunk(self, d):
        if self.bShouldProcessData and callable(self.callback):
            if self.rec.AcceptWaveform(bytes(d)):
                result = json.loads(self.rec.Result())['text'] + ""
                if len(result) > 0:
                    self.callback(result, True)
            else:
                result = json.loads(self.rec.PartialResult())['partial'] + ""
                if len(result) > 0:
                    self.callback(result, False)

    def HandleJob(self, job: str, *args, **kwargs):
        if job == 'toggle':
            self.bShouldProcessData = args[0]

    def run(self):
        global model_downloaded
        global model_downloading
        # https://alphacephei.com/vosk/models/vosk-model-en-us-daanzu-20200905.zip
        if not model_downloaded:
            if not path.exists(path.join(getcwd(), "model")):
                if model_downloading:
                    print('Waiting for another thread to download model', self.ident)
                    while model_downloading:
                        time.sleep(3)
                else:
                    model_downloading = True
                    print('downloading model', self.ident)

                    def OnProgress(t, c):
                        if callable(self.callback):
                            self.callback("Downloading Model {:.1f}/{:.1f} mb".format(float(c) * (1/1e+6), float(t) * (1/1e+6)),True)

                    download_url = "https://alphacephei.com/vosk/models/vosk-model-en-us-daanzu-20200905.zip"
                    dir_name = download_url.split('/')
                    dir_name.reverse()
                    dir_name = dir_name[0][:-4]
                    result = DownloadFile(download_url,OnProgress)
                    z = ZipFile(result)
                    z.extractall(getcwd())
                    z.close()
                    result.close()
                    os.rename(path.join(getcwd(),dir_name),path.join(getcwd(),'model'))
                    model_downloaded = True
                    model_downloading = False
            else:
                model_downloaded = True

        print(getcwd())
        self.model = Model(model_path=path.join(getcwd(),'model'))
        # r"C:\Users\Taree\Pictures\vosk-model-en-us-0.21\vosk-model-en-us-0.21")
        self.rec = KaldiRecognizer(self.model, self.samplerate_in)
        self.mic = StartVoice(callback=self.OnVoiceChunk, chunk=8000, samplerate_in=self.samplerate_in,
                              samplerate_out=self.samplerate_in, is_fft=False)
        if callable(self.onStart):
            self.onStart()



def StartSpeechRecognition(onVoiceData: Callable[[str, bool], None], onStart: Callable[[], None], samplerate_in=44100):
    SpeechRecognition = SpeechRecognitionThread(callback=onVoiceData, onStart=onStart, samplerate_in=samplerate_in)
    SpeechRecognition.start()
    return SpeechRecognition
