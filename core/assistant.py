import uuid
import importlib
import core.decorators
from core import constants
import re
from os import getcwd, listdir, path, mkdir
import sys
from core.events import gEmitter
from core.logger import log
from core.loops import CreateAsyncLoop
from core.singletons import Singleton, GetSingleton, SetSingleton
import asyncio
import importlib.util
import traceback
from pytz import timezone
from core.constants import \
    DIRECTORY_PLUGINS, \
    DIRECTORY_DATA, \
    SINGLETON_MAIN_LOADER_ID, \
    SINGLETON_INTENTS_INFERENCE_ID, \
    DIRECTORY_DATA_CORE_INTENTS_INFERENCE, \
    SINGLETON_ASSISTANT_ID, \
    SINGLETON_SKILL_MANAGER_ID, \
    WAKE_WORD
from core.neural.train import train_intents
from core.neural.inference import IntentInference


class SkillEvent:
    def __init__(self, skill_id, assistant, phrase) -> None:
        self.id = skill_id
        self.phrase = phrase
        self.assistant = assistant

    async def Respond(self, msg: str):
        await self.assistant.Respond(msg)


class Assistant(Singleton):

    def __init__(self):
        super().__init__(id=SINGLETON_ASSISTANT_ID)
        self.model_is_ready = False
        self.is_processing_command = False
        self.waiting_for_command = False
        self.is_following_up = False
        self.plugins = {}
        self.tz = timezone('US/Eastern')
        self.loop = CreateAsyncLoop()
        self.loader = GetSingleton(SINGLETON_MAIN_LOADER_ID)
        gEmitter.on(constants.EVENT_ON_FOLLOWUP_START, self.StartWaitFollowUp)
        gEmitter.on(constants.EVENT_ON_FOLLOWUP_END, self.StopWaitFollowUp)
        gEmitter.on(constants.EVENT_ON_SKILL_START, self.OnSkillStart)
        gEmitter.on(constants.EVENT_ON_SKILL_END, self.OnSkillEnd)
        gEmitter.on(constants.EVENT_SEND_PHRASE_TO_ASSISTANT, self.OnPhrase)
        self.RunAsync(self.LoadPlugins())

    def RunAsync(self, awaitable):
        return asyncio.run_coroutine_threadsafe(awaitable,
                                                self.loop)

    async def LoadPlugins(self):
        log('Loading Plugins')
        plugin_intents = []
        for plugin_dir in listdir(DIRECTORY_PLUGINS):

            LOAD_FILE = path.normpath(
                path.join(DIRECTORY_PLUGINS, plugin_dir, 'load.py'))

            if not path.exists(LOAD_FILE):
                continue

            try:
                sys.path.insert(0, path.join(DIRECTORY_PLUGINS, plugin_dir))

                spec = importlib.util.spec_from_file_location(
                    '{}.load'.format(plugin_dir), LOAD_FILE)
                imported_plugin = importlib.util.module_from_spec(spec)
                # sys.modules[spec.name] = module
                spec.loader.exec_module(imported_plugin)
                # imported_plugin = importlib.import_module(
                #     "plugins.{}.load".format(plugin_dir))

                plugin_id = imported_plugin.GetId()

                self.plugins[plugin_id] = imported_plugin

                plugin_intents.extend(imported_plugin.GetIntents())
                if not path.exists(path.join(DIRECTORY_DATA, plugin_id)):
                    mkdir(path.join(DIRECTORY_DATA, plugin_id))

                log(f'Imported Plugin :: {plugin_id}')
            except Exception as e:
                log('Error while Importing', LOAD_FILE)
                log(traceback.format_exc())
        log('Done Loading Plugins\n')
        log('Preparing Intents Inference')
        if not path.exists(DIRECTORY_DATA_CORE_INTENTS_INFERENCE):
            train_intents(plugin_intents,
                          DIRECTORY_DATA_CORE_INTENTS_INFERENCE)
        SetSingleton(SINGLETON_INTENTS_INFERENCE_ID,
                     IntentInference(DIRECTORY_DATA_CORE_INTENTS_INFERENCE))
        log('Done Preparing Intents Inference\n')
        await self.loader.LoadCurrent(self)

    def StartWaitFollowUp(self):
        self.is_following_up = True

    def StopWaitFollowUp(self):
        self.is_following_up = False

    def OnSkillStart(self, _):
        self.is_processing_command = True

    def OnSkillEnd(self, _):
        self.StopWaitFollowUp()
        self.is_processing_command = False

    async def Respond(self, msg: str):
        gEmitter.emit(constants.EVENT_ON_ASSISTANT_RESPONSE, msg)

    def OnPhrase(self, phrase: str, is_complete: bool, force_is_command=False):
        if self.is_following_up and is_complete:
            gEmitter.emit(constants.EVENT_ON_FOLLOWUP_MSG, phrase)

        if not self.is_processing_command and not self.is_following_up:
            has_wake_word = phrase.lower().strip().startswith(
                WAKE_WORD)
            if is_complete and (has_wake_word or force_is_command) and not self.waiting_for_command:
                phrase = phrase.lower()[len(WAKE_WORD):].strip()
                is_possible_command = len(phrase) > 0

                if is_possible_command:
                    # Try To start the associated skill
                    self.RunAsync(self.TryStartSkill(phrase))
                else:
                    # Put the assistant into waiting mode
                    self.waiting_for_command = True
                    self.Respond("Yes?")
            elif is_complete and self.waiting_for_command:
                if is_complete:
                    # Try To start the associated skill since we are already in waiting mode
                    self.RunAsync(self.TryStartSkill(phrase))
                    self.waiting_for_command = False

    async def TryStartSkill(self, phrase) -> list:
        try:
            parser = GetSingleton(SINGLETON_INTENTS_INFERENCE_ID)

            conf, intent = parser.GetIntent(phrase)

            log(phrase, conf, intent)
            skill_manger = GetSingleton(SINGLETON_SKILL_MANAGER_ID)

            if conf >= 0.8 and skill_manger.HasIntent(intent):
                skills = skill_manger.GetSkillsForIntent(intent)
                ids = []

                for func, reg in skills:
                    match = re.match(reg, phrase, re.IGNORECASE)

                    if match:
                        log(func)
                        skill_id = f"skill-{str(uuid.uuid4())}"

                        asyncio.create_task(func(SkillEvent(skill_id, self, phrase), match.groups()))
                        ids.append(skill_id)

                log(f'Phrase {phrase} Matched {len(ids)} Skills:',ids)
                return ids if len(ids) > 0 else None

            gEmitter.emit(constants.EVENT_ON_PHRASE_PARSE_ERROR)
        except Exception as e:
            log(e)
            log(traceback.format_exc())

        return None
