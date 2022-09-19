import wx
from constants import main_window_name, wx_color_darkgrey
from events import global_emitter
from threads.speech_recognition import StartSpeechRecognition
from ui.visualizer import Visualizer
from skills import *
from skills import TryRunCommand


class MainWindow(wx.Frame):

    def __init__(self):
        super(MainWindow, self).__init__(None, title=main_window_name, size=(1920 / 2, 1080 / 2))
        self.SetBackgroundColour(wx_color_darkgrey)
        self.model_is_ready = False
        self.speech_recognition = StartSpeechRecognition(onVoiceData=self.OnVoiceProcessed, onStart=self.OnVoiceStart)
        self.wake_word_detector = StartSpeechRecognition(onVoiceData=self.OnPossibleWakeWord, onStart=None)
        self.speech_recognition.AddJob('toggle', False)
        self.vis = Visualizer(self, bar_width=7, channels=16)
        global_emitter.on('window_action',self.DoSimpleWindowAction)

    def DoSimpleWindowAction(self,action:str):
        if action == "maximize":
            self.Maximize()
        elif action == "minimize":
            self.Iconize()
        elif action == "restore":
            self.Restore()

    def OnPossibleWakeWord(self, phrase: str, isComplete: bool):
        if isComplete and phrase.lower() == "assistant":
            global_emitter.emit('say', "Yes?", True)
            self.speech_recognition.AddJob('toggle', True)

    def OnVoiceProcessed(self, phrase: str, isComplete: bool):
        global_emitter.emit('say', phrase, isComplete)
        if self.model_is_ready:
            if isComplete:
                self.speech_recognition.AddJob('toggle', False)
                TryRunCommand(phrase)

    def OnVoiceStart(self):
        global_emitter.emit('say', 'Ready', True)
        self.model_is_ready = True
