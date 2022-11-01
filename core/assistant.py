import asyncio
import importlib
import json
import re
from os import getcwd, listdir, path
import sys
from core.constants import DATA_PATH, dynamic, config
from core.events import gEmitter
from core.singletons import Singleton, GetSingleton
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
    for skill_dir in listdir(SKILLS_PATH):
        sys.path.insert(0, path.join(SKILLS_PATH, skill_dir))
        for file in listdir(path.join(SKILLS_PATH, skill_dir)):
            if file.endswith('.json'):
                with open(path.join(SKILLS_PATH, skill_dir, file), 'r') as con_fig:
                    config_dict = json.load(con_fig)
                    nlu_combined.extend(config_dict['nlu'])
            elif file.endswith('.py') and file.startswith('skill_'):
                try:
                    impored_module = importlib.import_module(file[:-3])
                except Exception as e:
                    print('error while compiling', file)
                    print(traceback.format_exc())

                # with open(path.join(SKILLS_PATH, dir, file), 'r') as skill_f:
                #     try:
                #         exec(skill_f.read(), globals())
                #     except Exception as e:
                #         print('error while compiling', file)
                #         print(traceback.format_exc())

    current_hash = ""

    if path.exists(LATEST_HASH_PATH):
        with open(LATEST_HASH_PATH, 'r') as l_hash:
            current_hash = l_hash.readline()

    async with aiohttp.ClientSession() as session:
        data_to_send = {'version': '3.1', 'nlu': nlu_combined}
        async with session.post("https://proxy.oyintare.dev/nlu/train?h={}".format(current_hash),
                                data=json.dumps(data_to_send)) as resp:
            with open(LATEST_HASH_PATH, 'w') as l_hash_w:
                data = await resp.json()
                l_hash_w.write(data['data'])


def callTrain():
    asyncio.run_coroutine_threadsafe(TrainNlu(), loop=LOOP_FOR_ASYNC)


Thread(daemon=True, target=callTrain, group=None).start()


class Assistant(Singleton):

    def __init__(self):
        super().__init__(id='assistant')
        self.model_is_ready = False
        self.is_processing_command = False
        self.speaker = StartTTS()
        self.waiting_for_command = False
        self.is_following_up = False
        gEmitter.on('send_speech_voice', self.DoSpeech)
        gEmitter.on('start_follow_up', self.StartWaitFollowUp)
        gEmitter.on('stop_follow_up', self.StopWaitFollowUp)
        gEmitter.on('send_skill_start', self.OnSkillStart)
        gEmitter.on('send_skill_end', self.OnSkillEnd)
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

    def DoSpeech(self, message, callback):
        self.speaker.AddJob('speaker_tts', message, callback)

    def OnVoiceProcessed(self, phrase: str, is_complete: bool, force_is_command=False):
        if not self.is_processing_command:
            DisplayUiMessage(phrase)
        if self.is_following_up and is_complete:
            gEmitter.emit('follow_up', phrase)
        if not self.is_processing_command and not self.is_following_up:
            if is_complete and (phrase.lower().strip().startswith(
                    dynamic.wake_word) or force_is_command) and not self.waiting_for_command:
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

    async def TryStartSkill(self, phrase):
        try:
            parsed = await GetNluData(phrase)

            if not parsed:
                await TextToSpeech("I cannot answer that yet.", True)
                return

            skills = GetSingleton('skills')
            intent, confidence = parsed
            if confidence >= 0.89 and intent in skills.keys():
                skill, reg = skills[intent]
                match = re.match(reg, phrase, re.IGNORECASE)
                print(match, reg)
                if match:
                    await skill(self, phrase, match.groups())
                    return

            await TextToSpeech("I cannot answer that yet.", True)
        except Exception as e:
            print(e)
            print(traceback.format_exc())
        return
