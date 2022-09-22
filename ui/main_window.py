import wx
from constants import main_window_name, wx_color_darkgrey,wake_word
from events import global_emitter
from threads.say_text import StartTTS
from threads.speech_recognition import StartSpeechRecognition
from ui.visualizer import Visualizer
from skills import TryRunCommand


class MainWindow(wx.Frame):

    def __init__(self):
        super(MainWindow, self).__init__(None, title=main_window_name, size=(1920 / 2, 1080 / 2))
        self.SetBackgroundColour(wx_color_darkgrey)
        self.model_is_ready = False
        self.is_processing_command = False
        self.speaker = StartTTS()
        global_emitter.on('user_input',self.DoUserInput)
        self.speech_recognition = StartSpeechRecognition(onVoiceData=self.OnVoiceProcessed, onStart=self.OnVoiceStart)
        self.waiting_for_command = False
        self.vis = Visualizer(self, bar_width=7, channels=16)
        global_emitter.on('window_action',self.DoSimpleWindowAction)
        global_emitter.on('do_speech',self.DoSpeech)

    def DoSimpleWindowAction(self,action:str):
        if action == "maximize":
            self.Maximize()
        elif action == "minimize":
            self.Iconize()
        elif action == "restore":
            self.Restore()

    def DoUserInput(self,urs_input):
        self.OnVoiceProcessed(urs_input,True)
    def DoSpeech(self,message):
        self.speaker.AddJob('say', message)

    def OnVoiceProcessed(self, phrase: str, isComplete: bool):
        if not self.model_is_ready:
            global_emitter.emit('say', phrase, True)
            return
        if isComplete and phrase.lower().strip().startswith(wake_word) and not self.waiting_for_command:
            if len(phrase.lower()[len(wake_word):].strip()) > 0:
                self.is_processing_command = TryRunCommand(phrase.lower()[len(wake_word):].strip())
            else:
                self.waiting_for_command = True
                global_emitter.emit('do_speech', "Yes?")
                global_emitter.emit('say', "Listening...", True)
        elif isComplete and self.waiting_for_command:
            if isComplete:
                try:
                    TryRunCommand(phrase)
                except Exception as e:
                    print(e)
                self.waiting_for_command = False
        elif self.waiting_for_command:
            global_emitter.emit('say', phrase, False)

    def OnVoiceStart(self):
        global_emitter.emit('do_speech', "Speech Recognition Active.")
        global_emitter.emit('say', '...', True)
        self.model_is_ready = True

