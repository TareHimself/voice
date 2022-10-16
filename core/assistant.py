import asyncio
import json
from os import getcwd, listdir, path
import sys
from tempfile import tempdir
from core.constants import DATA_PATH, dynamic, config
from core.events import global_emitter
from core.skills import TryRunCommand
from core.threads import StartSpeechRecognition, StartTTS
from core.utils import TextToSpeech, DisplayUiMessage, GetFileHash
from threading import Thread
import asyncio
import aiohttp
import traceback

LOOP_FOR_ASYNC = asyncio.new_event_loop()
LATEST_HASH_PATH = path.join(DATA_PATH, 'nlu.sha')
BASE_NLU_PATH = path.join(getcwd(), 'nlu.yml')


def RunLoop():
    LOOP_FOR_ASYNC.run_forever()


LoopThread = Thread(daemon=True, target=RunLoop, group=None)
LoopThread.start()

SKILLS_PATH = path.join(getcwd(), 'skills')
nlu_combined = []


async def TrainNlu():

    for dir in listdir(SKILLS_PATH):
        sys.path.insert(0, path.join(SKILLS_PATH, dir))
        for file in listdir(path.join(SKILLS_PATH, dir)):
            if file.endswith('.json'):
                with open(path.join(SKILLS_PATH, dir, file), 'r') as con_fig:
                    config_dict = json.load(con_fig)
                    nlu_combined.extend(config_dict['nlu'])
            elif file.endswith('.py') and file.startswith('skill_'):
                with open(path.join(SKILLS_PATH, dir, file), 'r') as skill_f:
                    try:
                        exec(skill_f.read(), globals())
                    except Exception as e:
                        print('error while compiling', file)
                        print(traceback.format_exc())

    current_hash = ""

    if path.exists(LATEST_HASH_PATH):
        with open(LATEST_HASH_PATH, 'r') as l_hash:
            current_hash = l_hash.readline()

    async with aiohttp.ClientSession() as session:
        data_to_send = {'version': '3.1', 'nlu': nlu_combined}
        async with session.post("http://localhost:8097/train?h={}".format(current_hash), data=json.dumps(data_to_send)) as resp:
            with open(LATEST_HASH_PATH, 'w') as l_hash_w:
                data = await resp.json()
                l_hash_w.write(data['data'])


def callTrain():
    asyncio.run_coroutine_threadsafe(TrainNlu(), loop=LOOP_FOR_ASYNC)


Thread(daemon=True, target=callTrain, group=None).start()


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
        self.speech_recognition = StartSpeechRecognition(
            onVoiceData=self.OnVoiceProcessed, onStart=self.OnVoiceStart)

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

    def OnVoiceProcessed(self, phrase: str, is_complete: bool, assumeIsCommand=False):
        if not self.is_processing_command:
            DisplayUiMessage(phrase)
        if self.is_following_up and is_complete:
            global_emitter.emit('follow_up', phrase)
        if not self.is_processing_command and not self.is_following_up:
            if is_complete and (phrase.lower().strip().startswith(dynamic.wake_word) or assumeIsCommand) and not self.waiting_for_command:
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
