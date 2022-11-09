import json
import os
import time
from io import BytesIO
from typing import Callable
import requests
from tqdm import tqdm
from vosk import Model, KaldiRecognizer, SetLogLevel
from os import getcwd, path
from core.events import gEmitter, ThreadEmitter
from core.logger import log
from core.threads.voice import StartVoice
from core.threads.collect_input import InputThread
from zipfile import ZipFile
from core.constants import DIRECTORY_DATA
from core.events import gEmitter
from core.decorators import AssistantLoader
from core import constants
from plugins.base.constants import PLUGIN_ID

VOSK_MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-en-us-daanzu-20200905.zip"
MODEL_DOWNLOAD_PATH = path.join(DIRECTORY_DATA, PLUGIN_ID, 'stt')


def DownloadFile(url: str, OnProgress: Callable[[int, int], None] = lambda t, p: None):
    f = BytesIO()
    r = requests.get(url, stream=True)
    total = r.headers["Content-Length"]

    for chunk in r.iter_content(1024):
        f.write(chunk)
        OnProgress(total, f.getbuffer().nbytes)

    return f


SetLogLevel(-1)

model_downloaded = False
model_downloading = False

SHOULD_USE_INPUT = False


class SpeechRecognitionThread(ThreadEmitter):

    def __init__(self, callback=0, onStart=0, samplerate_in=16000, device=None):
        super(SpeechRecognitionThread, self).__init__()
        self.device = None
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

    def OnInputFromUser(self, msg):
        if callable(self.callback):
            self.callback(msg, True, True)

    def run(self):
        gEmitter.on('user_input', self.OnInputFromUser)

        if SHOULD_USE_INPUT:
            i = InputThread()
            i.start()
        else:
            self.model = Model(model_path=MODEL_DOWNLOAD_PATH)
            self.rec = KaldiRecognizer(self.model, self.samplerate_in)
            self.mic = StartVoice(callback=self.OnVoiceChunk,
                                  chunk=8000, samplerate=self.samplerate_in, device=self.device)

        if callable(self.onStart):
            self.onStart()


@AssistantLoader(loader_id='base-speech-recognition')
async def DownloadAndStartModel(va):

    if not path.exists(MODEL_DOWNLOAD_PATH):
        download_progress = None
        last_c = 0

        def OnProgress(t, c):
            t = float(t)
            c = float(c)
            nonlocal last_c
            nonlocal download_progress
            if not download_progress:
                download_progress = tqdm(
                    total=t, unit='B', unit_scale=True, desc="Downloading Speech To Text Model")

            download_progress.update(c - last_c)
            last_c = c
        download_url = VOSK_MODEL_URL
        dir_name = download_url.split('/')
        dir_name.reverse()
        dir_name = dir_name[0][:-4]
        result = DownloadFile(download_url, OnProgress)
        z = ZipFile(result)
        EXTRACT_PATH = path.join(DIRECTORY_DATA, PLUGIN_ID)
        z.extractall(EXTRACT_PATH)
        z.close()
        result.close()
        os.rename(path.join(EXTRACT_PATH, dir_name),
                  MODEL_DOWNLOAD_PATH)

    def OnCallback(phrase, is_complete):
        log(phrase, is_complete)
        gEmitter.emit(constants.EVENT_SEND_PHRASE_TO_ASSISTANT,
                      phrase, is_complete)

    SpeechRecognitionThread(
        callback=OnCallback, onStart=lambda: log('Speech Recognition Active'), device=1).start()
