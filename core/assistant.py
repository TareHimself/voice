import uuid
import importlib
import core.decorators
from core import constants
import re
from os import listdir, path, mkdir
import sys
from core.events import gEmitter
from core.logger import log
from core.loops import create_async_loop
from core.singletons import Singleton, get_singleton, set_singleton
import asyncio
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
from core.neural.engines import IntentsEngine
from typing import Any, Callable, Coroutine, Union
from core.threads.timer import start_timer, stop_timer


class AssistantContext:
    def __init__(self) -> None:
        pass

    async def get_followup(self, timeout_secs=0) -> Union[str, None]:
        loop = asyncio.get_event_loop()
        task_return = asyncio.Future()
        task_id = uuid.uuid1()
        status = 0

        def on_results_recieved(msg):
            nonlocal status
            nonlocal task_return

            if status == 0:
                stop_timer(task_id)
                gEmitter.off(constants.EVENT_ON_FOLLOWUP_MSG,
                             on_results_recieved)
                loop.call_soon_threadsafe(task_return.set_result, msg)
                gEmitter.emit(constants.EVENT_ON_FOLLOWUP_END)
                status = 1

        def OnTimeout():
            nonlocal status
            nonlocal task_return
            if status == 0:
                gEmitter.off(constants.EVENT_ON_FOLLOWUP_MSG,
                             on_results_recieved)
                loop.call_soon_threadsafe(task_return.set_result, None)
                gEmitter.emit(constants.EVENT_ON_FOLLOWUP_END)
                status = 1

        gEmitter.on(constants.EVENT_ON_FOLLOWUP_MSG, on_results_recieved)

        gEmitter.emit(constants.EVENT_ON_FOLLOWUP_START)
        if timeout_secs > 0:
            start_timer(timer_id=task_id, length=timeout_secs,
                        callback=OnTimeout)

        result = await task_return

        return result

    async def handle_response(self, resp: str):
        gEmitter.emit(constants.EVENT_ON_ASSISTANT_RESPONSE, resp)

    async def handle_parse_error(self, phrase: str):
        gEmitter.emit(constants.EVENT_ON_PHRASE_PARSE_ERROR)


class SkillEvent:
    def __init__(self, skill_id,intent:str, assistant: 'Assistant', phrase, context: AssistantContext) -> None:
        self.id = skill_id
        self.phrase = phrase
        self.assistant = assistant
        self.context = context
        self.intent = intent


class Assistant(Singleton):

    def __init__(self):
        super().__init__(id=SINGLETON_ASSISTANT_ID)
        self.model_is_ready = False
        self.is_processing_command = False
        self.waiting_for_command = False
        self.is_following_up = False
        self.plugins = {}
        self.tz = timezone('US/Eastern')
        self.loop = create_async_loop()
        self.loader = get_singleton(SINGLETON_MAIN_LOADER_ID)
        gEmitter.on(constants.EVENT_ON_FOLLOWUP_START,
                    self.start_wait_follow_up)
        gEmitter.on(constants.EVENT_ON_FOLLOWUP_END, self.stop_wait_follow_up)
        gEmitter.on(constants.EVENT_ON_SKILL_START, self.on_skill_start)
        gEmitter.on(constants.EVENT_ON_SKILL_END, self.on_skill_end)
        gEmitter.on(constants.EVENT_SEND_PHRASE_TO_ASSISTANT, self.on_phrase)
        self.run_async(self.load_plugins())

    def run_async(self, awaitable):
        return asyncio.run_coroutine_threadsafe(awaitable,
                                                self.loop)

    async def load_plugins(self):
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

                plugin_intents.extend(imported_plugin.get_intents())
                if not path.exists(path.join(DIRECTORY_DATA, plugin_id)):
                    mkdir(path.join(DIRECTORY_DATA, plugin_id))

                log(f'Imported Plugin :: {plugin_id}')
            except Exception as e:
                log('Error while Importing', LOAD_FILE)
                log(traceback.format_exc())
        log('Done Loading Plugins\n')
        log('Preparing Intents Inference')

        set_singleton(SINGLETON_INTENTS_INFERENCE_ID,
                      IntentsEngine(plugin_intents,DIRECTORY_DATA_CORE_INTENTS_INFERENCE))
        log('Done Preparing Intents Inference\n')
        await self.loader.load_current(self)

    def start_wait_follow_up(self):
        self.is_following_up = True

    def stop_wait_follow_up(self):
        self.is_following_up = False

    def on_skill_start(self, _):
        self.is_processing_command = True

    def on_skill_end(self, _):
        self.stop_wait_follow_up()
        self.is_processing_command = False

    async def on_phrase(self, phrase: str, is_complete: bool, force_is_command=False):
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
                    self.run_async(self.try_start_skill(phrase))
                else:
                    # Put the assistant into waiting mode
                    self.waiting_for_command = True
                    self.Respond("Yes?")
            elif is_complete and self.waiting_for_command:
                if is_complete:
                    # Try To start the associated skill since we are already in waiting mode
                    self.run_async(self.try_start_skill(phrase))
                    self.waiting_for_command = False

    async def try_start_skill(self, phrase, context=AssistantContext, *args) -> list:
        try:

            parser: IntentsEngine = get_singleton(
                SINGLETON_INTENTS_INFERENCE_ID)

            conf, intent = parser.get_intent(phrase)

            skill_manager: core.decorators.SkillManager = get_singleton(
                SINGLETON_SKILL_MANAGER_ID)

            handler = context(*args)

            if skill_manager.can_start_skills_in_context(context):
                log("Attempting to start skills in context ",conf, intent,skill_manager.has_intent(intent))
                if conf >= 0.8 and skill_manager.has_intent(intent):
                    skills = skill_manager.get_skills_for_intent(intent)
                    ids = []

                    for func, reg in skills:
                        match = re.match(reg, phrase, re.IGNORECASE)

                        if match:          
                            skill_id = f"skill-{str(uuid.uuid4())}"

                            asyncio.create_task(
                                func(SkillEvent(skill_id, intent ,self, phrase, handler), match.groups()))
                            ids.append(skill_id)

                    log(f'Phrase {phrase} Matched {len(ids)} Skills:', ids)
                    return ids if len(ids) > 0 else None
                await handler.handle_parse_error(
                    "Sorry i didn't understand that.")
        except Exception as e:
            log(e)
            log(traceback.format_exc())

        return None
