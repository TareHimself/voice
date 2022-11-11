import asyncio
from typing import Union
from core.decorators import AssistantLoader
from core.events import gEmitter
from core import constants
import os
from os import path
import torch
import sounddevice as sd
from core.events import ThreadEmitter
from core.logger import log
from core.constants import DIRECTORY_DATA
from plugins.base.constants import PLUGIN_ID
device = torch.device('cpu')
torch.set_num_threads(8)

SAMPLE_RATE = 48000
TTS_SPEAKER = 'en_10'
TTS_URL = 'https://models.silero.ai/models/tts/en/v3_en.pt'
TTS_DIR = path.join(DIRECTORY_DATA, PLUGIN_ID, 'tts.pt')
CHANNELS = 1
INPUT_DEVICE = None  # 4


class TTSThread(ThreadEmitter):

    def __init__(self):
        super().__init__()
        self.model = None

    def DoTTS(self, text, callback):
        if self.model:
            audio = self.model.apply_tts(text=text,
                                         speaker=TTS_SPEAKER,
                                         sample_rate=SAMPLE_RATE)
            if callable(callback):
                sd.play(audio, SAMPLE_RATE, blocking=True)
                callback()
            else:
                sd.play(audio, SAMPLE_RATE)

    def HandleJob(self, job: str, *args, **kwargs):
        if job == 'tts':
            self.DoTTS(*args, *kwargs)

    def run(self):
        self.model = torch.package.PackageImporter(
            TTS_DIR).load_pickle("tts_models", "model")
        self.model.to(device)
        while True:
            self.ProcessJobs()


async def TextToSpeech(msg, waitForFinish=False):
    if not waitForFinish:
        gEmitter.emit('base-do-speech', msg, None)
        return

    loop = asyncio.get_event_loop()
    task_return = asyncio.Future()

    def OnFinish():
        nonlocal task_return
        loop.call_soon_threadsafe(task_return.set_result, None)

    gEmitter.emit('base-do-speech', msg, OnFinish)

    await task_return
    return


@AssistantLoader(loader_id='base-tts')
async def LoadTTS():
    if not os.path.isfile(TTS_DIR):
        torch.hub.download_url_to_file(TTS_URL,
                                       TTS_DIR)

    tts = TTSThread()
    tts.start()

    def SendSpeech(msg, callback):
        tts.AddJob('tts', msg, callback)

    gEmitter.on(constants.EVENT_ON_PHRASE_PARSE_ERROR,
                lambda: asyncio.run(TextToSpeech('I cannot answer that yet.')))
    gEmitter.on('base-do-speech', SendSpeech)

    await TextToSpeech('Base Speech Active.')
