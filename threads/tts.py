# V3
import os
import torch
import sounddevice as sd
from events.thread_emitter import ThreadEmitter
from constants import tts_speaker,tts_filename,tts_url
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
            print('start apply',text)
            audio = self.model.apply_tts(text=text,
                                         speaker=tts_speaker,
                                         sample_rate=SAMPLE_RATE)
            print('finish apply',text)


            sd.play(audio,SAMPLE_RATE);

    def HandleJob(self, job: str, *args, **kwargs):
        if job == 'speaker_tts':
            self.DoTTS(*args, *kwargs)

    def run(self):
        if not os.path.isfile(tts_filename):
            torch.hub.download_url_to_file(tts_url,
                                           tts_filename)
        self.model = torch.package.PackageImporter(tts_filename).load_pickle("tts_models", "model")
        self.model.to(device)
        while True:
            self.ProcessJobs()


def StartTTS():
    tts = TTSThread()
    tts.start()
    return tts
