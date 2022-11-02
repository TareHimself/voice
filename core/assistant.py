import asyncio
import importlib
import json
import re
from os import getcwd, listdir, path
import sys
from core.constants import DATA_PATH, dynamic, config
from core.decorators import AssistantLoader
from core.events import gEmitter
from core.logger import log
from core.loops import CreateAsyncLoop
from core.singletons import Singleton, GetSingleton
from core.skills import TryRunCommand
from core.threads import StartSpeechRecognition, StartTTS
from core.utils import TextToSpeech, DisplayUiMessage, GetFileHash
from threading import Thread
import asyncio
import aiohttp
import traceback


LATEST_HASH_PATH = path.join(DATA_PATH, 'nlu.sha')
BASE_NLU_PATH = path.join(getcwd(), 'nlu.yml')


SKILLS_PATH = path.join(getcwd(), 'skills')
nlu_combined = []


@AssistantLoader
async def LoadSkills(va):
    log('Loading Skills')
    for skill_dir in listdir(path.normpath(SKILLS_PATH)):
        sys.path.insert(0, path.normpath(path.join(SKILLS_PATH, skill_dir)))
        for file in listdir(path.normpath(path.join(SKILLS_PATH, skill_dir))):
            if file.endswith('.json'):
                with open(path.normpath(path.join(SKILLS_PATH, skill_dir, file)), 'r') as con_fig:
                    config_dict = json.load(con_fig)
                    nlu_combined.extend(config_dict['intents'])
            elif file.endswith('.py') and file.startswith('skill_'):
                try:
                    impored_module = importlib.import_module(file[:-3])
                    log('Imported Module', impored_module.__name__)
                except Exception as e:
                    log('error while compiling', file)
                    log(traceback.format_exc())

                # with open(path.join(SKILLS_PATH, dir, file), 'r') as skill_f:
                #     try:
                #         exec(skill_f.read(), globals())
                #     except Exception as e:
                #         log('error while compiling', file)
                #         log(traceback.format_exc())

    log('Done Loading Skills')


class SkillEvent:
    def __init__(self, assistant, phrase) -> None:
        self.phrase = phrase
        self.assistant = assistant


class Assistant(Singleton):

    def __init__(self):
        super().__init__(id='assistant')
        self.model_is_ready = False
        self.is_processing_command = False
        self.speaker = StartTTS()
        self.waiting_for_command = False
        self.is_following_up = False
        self.loop = CreateAsyncLoop()
        self.loader = GetSingleton("main-loader")
        gEmitter.on('send_speech_voice', self.DoSpeech)
        gEmitter.on('start_follow_up', self.StartWaitFollowUp)
        gEmitter.on('stop_follow_up', self.StopWaitFollowUp)
        gEmitter.on('send_skill_start', self.OnSkillStart)
        gEmitter.on('send_skill_end', self.OnSkillEnd)
        self.RunAsync(self.loader.LoadCurrent(self))
        self.speech_recognition = StartSpeechRecognition(
            onVoiceData=self.OnVoiceProcessed, onStart=self.OnVoiceStart)

    def RunAsync(self, awaitable):
        return asyncio.run_coroutine_threadsafe(awaitable,
                                                self.loop)

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
                phrase = phrase.lower()[len(dynamic.wake_word):].strip()
                if len(phrase) > 0:
                    self.RunAsync(self.TryStartSkill(phrase))
                else:
                    self.waiting_for_command = True
                    TextToSpeech("Yes?")
                    DisplayUiMessage("Listening...")
            elif is_complete and self.waiting_for_command:
                if is_complete:
                    try:
                        self.RunAsync(self.TryStartSkill(phrase))
                    except Exception as e:
                        log(e)
                    self.waiting_for_command = False

    def OnVoiceStart(self):
        TextToSpeech("Speech Recognition Active.")
        DisplayUiMessage('...')
        self.model_is_ready = True

    async def TryStartSkill(self, phrase):
        try:
            phrase_intent, confidence = "skill_none", 0.5
            parsed = ""  # await GetNluData(phrase)

            if phrase_intent == "skill_none":
                await TextToSpeech("I cannot answer that yet.", True)
                return

            skills = GetSingleton('skills')

            intent, confidence = parsed
            if confidence >= 0.89 and intent in skills.keys():
                skill, reg = skills[intent]
                match = re.match(reg, phrase, re.IGNORECASE)
                log(match, reg)
                if match:
                    await skill(SkillEvent(self, phrase), match.groups())
                    return

            await TextToSpeech("I cannot answer that yet.", True)
        except Exception as e:
            log(e)
            log(traceback.format_exc())
        return
