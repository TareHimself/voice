import asyncio
import threading

from core.constants import dynamic
from core.events import global_emitter
from core.skills import TryRunCommand
from core.threads import StartSpeechRecognition,StartTTS
from core.utils import TextToSpeech, DisplayUiMessage
from threading import Thread

LOOP_FOR_ASYNC = asyncio.new_event_loop()


def RunLoop():
    LOOP_FOR_ASYNC.run_forever()


LoopThread = Thread(daemon=True, target=RunLoop, group=None)
LoopThread.start()


class Assistant:

    def __init__(self):
        self.model_is_ready = False
        self.is_processing_command = False
        self.speaker = StartTTS()
        self.waiting_for_command = False
        self.is_following_up = False
        global_emitter.on('send_speech_voice', self.DoSpeech)
        global_emitter.on('start_follow_up', self.StartWaitFollowUp)
        global_emitter.on('stop_follow_up', self.StopWaitFollowUp)
        global_emitter.on('send_skill_start', self.OnSkillStart)
        global_emitter.on('send_skill_end', self.OnSkillEnd)
        self.speech_recognition = StartSpeechRecognition(onVoiceData=self.OnVoiceProcessed, onStart=self.OnVoiceStart)

    def StartWaitFollowUp(self):
        self.is_following_up = True

    def StopWaitFollowUp(self):
        self.is_following_up = False

    def OnSkillStart(self):
        self.is_processing_command = True

    def OnSkillEnd(self):
        DisplayUiMessage('...')
        self.StopWaitFollowUp()
        self.is_processing_command = False

    def DoSpeech(self, message):
        self.speaker.AddJob('speaker_tts', message)

    def OnVoiceProcessed(self, phrase: str, is_complete: bool):
        print(phrase)
        if not self.is_processing_command:
            DisplayUiMessage(phrase)
        if self.is_following_up and is_complete:
            global_emitter.emit('follow_up', phrase)
        if not self.is_processing_command and not self.is_following_up:
            if is_complete and phrase.lower().strip().startswith(dynamic.wake_word) and not self.waiting_for_command:
                if len(phrase.lower()[len(dynamic.wake_word):].strip()) > 0:
                    asyncio.run_coroutine_threadsafe(TryRunCommand(phrase.lower()[len(dynamic.wake_word):].strip()),
                                                     LOOP_FOR_ASYNC)
                else:
                    self.waiting_for_command = True
                    TextToSpeech("Yes?")
                    DisplayUiMessage("Listening...")
            elif is_complete and self.waiting_for_command:
                if is_complete:
                    try:
                        asyncio.run_coroutine_threadsafe(TryRunCommand(phrase),
                                                         LOOP_FOR_ASYNC)
                    except Exception as e:
                        print(e)
                    self.waiting_for_command = False

    def OnVoiceStart(self):
        TextToSpeech("Speech Recognition Active.")
        DisplayUiMessage('...')
        self.model_is_ready = True


