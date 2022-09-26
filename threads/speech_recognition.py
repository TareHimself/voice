import json
import os
import time
from typing import Callable
from vosk import Model, KaldiRecognizer, SetLogLevel
from os import getcwd, path, mkdir, listdir
from constants import vosk_model_url
from events import global_emitter
from events.thread_emitter import ThreadEmitter
from threads.voice import StartVoice
from zipfile import ZipFile
from threads.collect_input import InputThread
from utils import DownloadFile

SetLogLevel(-1)

model_downloaded = False
model_downloading = False

SHOULD_USE_INPUT = False

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

    def OnInputFromUser(self,msg):
        if callable(self.callback):
            self.callback(msg, True)

    def run(self):
        if SHOULD_USE_INPUT:
            i = InputThread()
            i.start()
            global_emitter.on('user_input',self.OnInputFromUser)
        else:
            global model_downloaded
            global model_downloading
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

                        download_url = vosk_model_url
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

            self.model = Model(model_path=path.join(getcwd(),'model'))
            self.rec = KaldiRecognizer(self.model, self.samplerate_in)
            self.mic = StartVoice(callback=self.OnVoiceChunk, chunk=8000, samplerate_in=self.samplerate_in,
                                  samplerate_out=self.samplerate_in, is_fft=False)


        if callable(self.onStart):
            self.onStart()

def StartSpeechRecognition(onVoiceData: Callable[[str, bool], None], onStart: Callable[[], None], samplerate_in=44100):
    SpeechRecognition = SpeechRecognitionThread(callback=onVoiceData, onStart=onStart, samplerate_in=samplerate_in)
    SpeechRecognition.start()
    return SpeechRecognition
