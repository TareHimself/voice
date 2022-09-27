import asyncio
import threading

from constants import wake_word
from events import global_emitter
from skills import GetCommand
from threads.speech_recognition import StartSpeechRecognition
from threads.tts import StartTTS
from utils import TextToSpeech, DisplayUiMessage


class Assistant:

    def __init__(self):
        self.model_is_ready = False
        self.is_processing_command = False
        self.speaker = StartTTS()
        self.waiting_for_command = False
        self.is_following_up = False
        global_emitter.on('send_speech_voice', self.DoSpeech)
        global_emitter.on('start_wait_followup', self.StartWaitFollowUp)
        global_emitter.on('stop_wait_followup', self.StopWaitFollowUp)
        global_emitter.on('send_command_end', self.OnCommandEnd)
        self.speech_recognition = StartSpeechRecognition(onVoiceData=self.OnVoiceProcessed, onStart=self.OnVoiceStart)

    def StartWaitFollowUp(self):
        self.is_following_up = True

    def StopWaitFollowUp(self):
        self.is_following_up = False

    def OnCommandEnd(self):
        DisplayUiMessage('...')
        self.StopWaitFollowUp()
        self.is_processing_command = False

    def DoSpeech(self, message):
        self.speaker.AddJob('speaker_tts', message)

    def OnVoiceProcessed(self, phrase: str, is_complete: bool):

        if not self.is_processing_command:
            DisplayUiMessage(phrase)

        if self.is_following_up and is_complete:
            global_emitter.emit('send_followup_text', phrase)
        if not self.is_processing_command and not self.is_following_up:
            if is_complete and phrase.lower().strip().startswith(wake_word) and not self.waiting_for_command:
                if len(phrase.lower()[len(wake_word):].strip()) > 0:
                    command = GetCommand(phrase.lower()[len(wake_word):].strip())
                    if command is not None:
                        self.is_processing_command = True
                        func, arg1, arg2 = command
                        func(arg1, arg2)
                else:
                    self.waiting_for_command = True
                    TextToSpeech("Yes?")
                    DisplayUiMessage("Listening...")
            elif is_complete and self.waiting_for_command:
                if is_complete:
                    try:
                        command = GetCommand(phrase)
                        if command is not None:
                            self.is_processing_command = True
                            func, arg1, arg2 = command
                            func(arg1, arg2)
                    except Exception as e:
                        print(e)
                    self.waiting_for_command = False


    def OnVoiceStart(self):
        TextToSpeech("Speech Recognition Active.")
        DisplayUiMessage('...')
        self.model_is_ready = True

    """
    def OnVoiceProcessed(self, phrase: str, is_complete: bool):
        print(phrase)
        if not self.model_is_ready:
            DisplayUiMessage(phrase)
            return
        if self.is_following_up and is_complete:
            global_emitter.emit('send_followup_text', phrase)
        if not self.is_processing_command and not self.is_following_up:
            if is_complete and phrase.lower().strip().startswith(wake_word) and not self.waiting_for_command:
                if len(phrase.lower()[len(wake_word):].strip()) > 0:
                    command = GetCommand(phrase.lower()[len(wake_word):].strip())
                    if command is not None:
                        self.is_processing_command = True
                        func, arg1, arg2 = command
                        func(arg1, arg2)

                else:
                    self.waiting_for_command = True
                    TextToSpeech("Yes?")
                    DisplayUiMessage("Listening...")
            elif is_complete and self.waiting_for_command:
                if is_complete:
                    try:
                        command = GetCommand(phrase)
                        if command is not None:
                            self.is_processing_command = True
                            func, arg1, arg2 = command
                            func(arg1, arg2)
                    except Exception as e:
                        print(e)
                    self.waiting_for_command = False
        elif self.waiting_for_command and not self.is_following_up:
            DisplayUiMessage(phrase)
            """