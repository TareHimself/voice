import json
from os import path,getcwd
import wx
SECRETS_PATH = path.join(getcwd(),'secrets.json')

tts_filename = 'tts_model.pt'
tts_speaker = 'en_10'
tts_url = 'https://models.silero.ai/models/tts/en/v3_en.pt'

vosk_model_url = "https://alphacephei.com/vosk/models/vosk-model-en-us-daanzu-20200905.zip"
wx_color_darkgrey = wx.Colour(31, 31, 31)
wx_visualizer_band_color = wx.Colour(255, 255, 255)
main_window_name = "Voice"
wake_word ="alice"
secrets = {}
with open(SECRETS_PATH, "r") as infile:
    secrets = json.load(infile)


