# V3
import os
import torch
import sounddevice as sd
from core.events import ThreadEmitter
from core.constants import TTS_SPEAKER,TTS_PATH,TTS_URL
device = torch.device('cpu')
torch.set_num_threads(8)
SAMPLE_RATE = 48000



CHANNELS = 1
INPUT_DEVICE = None  # 4


class TTSThread(ThreadEmitter):

    def __init__(self):
        super(TTSThread, self).__init__()
        self.model = None

    def DoTTS(self, text):
        if self.model:
            audio = self.model.apply_tts(text=text,
                                         speaker=TTS_SPEAKER,
                                         sample_rate=SAMPLE_RATE)
            sd.play(audio,SAMPLE_RATE);

    def HandleJob(self, job: str, *args, **kwargs):
        if job == 'speaker_tts':
            self.DoTTS(*args, *kwargs)

    def run(self):
        if not os.path.isfile(TTS_PATH):
            torch.hub.download_url_to_file(TTS_URL,
                                           TTS_PATH)
        self.model = torch.package.PackageImporter(TTS_PATH).load_pickle("tts_models", "model")
        self.model.to(device)
        while True:
            self.ProcessJobs()


def StartTTS():
    tts = TTSThread()
    tts.start()
    return tts
