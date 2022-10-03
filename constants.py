import json
from os import path, getcwd, mkdir
import wx

SECRETS_PATH = path.join(getcwd(), 'secrets.json')

DATA_PATH = path.join(getcwd(), 'data')

if not path.exists(DATA_PATH):
    mkdir(DATA_PATH)

TTS_DIR = path.join(DATA_PATH, 'tts_model.pt')
STT_DIR = path.join(DATA_PATH, 'stt_model')
NLU_DIR = path.join(DATA_PATH, 'nlu.tar.gz')
TTS_SPEAKER = 'en_10'
TTS_URL = 'https://models.silero.ai/models/tts/en/v3_en.pt'
VOSK_MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-en-us-daanzu-20200905.zip"
main_window_name = "Voice"

secrets = {}
with open(SECRETS_PATH, "r") as infile:
    secrets = json.load(infile)


class DynamicData:
    def __init__(self):
        self.wake_word = "alice"
        self.wx_color_darkgrey = wx.Colour(31, 31, 31)
        self.wx_visualizer_band_color = wx.Colour(255, 255, 255)


dynamic = DynamicData()
