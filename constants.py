import json
from os import path,getcwd
import wx
SECRETS_PATH = path.join(getcwd(),'secrets.json')

vosk_model_url = "https://alphacephei.com/vosk/models/vosk-model-en-us-daanzu-20200905.zip"
wx_color_darkgrey = wx.Colour(31, 31, 31)
wx_visualizer_band_color = wx.Colour(255, 255, 255)
main_window_name = "Voice"
wake_word ="smart"
secrets = {}
with open(SECRETS_PATH, "r") as infile:
    secrets = json.load(infile)
