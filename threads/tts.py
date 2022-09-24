# V3
import os
import torch
import sounddevice as sd
from events.thread_emitter import ThreadEmitter

device = torch.device('cpu')
torch.set_num_threads(4)
local_file = 'tts_model.pt'
SAMPLE_RATE = 48000
SPEAKER = 'en_10'


CHANNELS = 1
INPUT_DEVICE = None  # 4


class TTSThread(ThreadEmitter):

    def __init__(self):
        super(TTSThread, self).__init__()
        self.model = None

    def DoTTS(self, text):
        if self.model:
            audio = self.model.apply_tts(text=text,
                                         speaker=SPEAKER,
                                         sample_rate=SAMPLE_RATE)

            sd.play(audio,SAMPLE_RATE);

    def HandleJob(self, job: str, *args, **kwargs):
        if job == 'speaker_tts':
            self.DoTTS(*args, *kwargs)

    def run(self):
        if not os.path.isfile(local_file):
            torch.hub.download_url_to_file('https://models.silero.ai/models/tts/en/v3_en.pt',
                                           local_file)
        self.model = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")
        self.model.to(device)
        while True:
            self.ProcessJobs()


def StartTTS():
    tts = TTSThread()
    tts.start()
    return tts
