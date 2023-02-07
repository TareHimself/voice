import re
import traceback
import uuid
import inspect
from core.constants import SINGLETON_SERVER_ID, SINGLETON_MAIN_LOADER_ID, SINGLETON_SKILL_MANAGER_ID, \
    EVENT_ON_SKILL_START, EVENT_ON_SKILL_END
from core.logger import log
from core.singletons import get_singleton, Singleton, set_singleton
from core.events import GLOBAL_EMITTER
import inspect
import os


class MainLoader(Singleton):
    def __init__(self):
        super().__init__(id=SINGLETON_MAIN_LOADER_ID)
        self.loaders = {}

    def __len__(self):
        return len(self.loaders.values())

    def add_loader(self, id, loader, plugin_dir=None):
        if id not in self.loaders.keys():
            self.loaders[id] = [loader, plugin_dir]

    async def load_current(self, va):
        items = list(self.loaders.keys())

        for id in items:
            try:
                loader_func, plugin_path = self.loaders[id]
                params_count = len(inspect.signature(loader_func).parameters)

                if params_count == 0:
                    await loader_func()
                elif params_count == 1:
                    await loader_func(va)
                else:
                    await loader_func(va, va.plugins.get(plugin_path, None))
                del self.loaders[id]
            except Exception as e:
                log(f"Error Loading {id} ::", e)
            log("Loaded", id)

        if len(self.loaders.keys()):
            await self.load_current(va)


MAIN_LOADER = MainLoader()


def AssistantLoader(loader_id=""):

    abs_path = os.path.abspath((inspect.stack()[1])[1])
    plugin_base_dir = None
    match = re.match(
        r"(.*plugins[\\\/].*?)[\\\/]", abs_path)
    if match is not None:
        plugin_base_dir = match.groups()[0]

    if callable(loader_id):
        MAIN_LOADER.add_loader(
            "loader-{}".format(uuid.uuid4()), loader_id, plugin_base_dir)
        return loader_id

    def wrapper(func):
        nonlocal loader_id
        nonlocal plugin_base_dir
        MAIN_LOADER.add_loader(loader_id, func, plugin_base_dir)
        return func

    return wrapper


class SkillManager(Singleton):
    def __init__(self):
        super().__init__(id=SINGLETON_SKILL_MANAGER_ID)
        self.all_skills = {}
        self.active_skills = {}
        self.active_contexts = {}

    def add_skill(self, intent, wrapped_skill, params_regex, plugin_dir):
        if not self.has_intent(intent):
            self.all_skills[intent] = []

        self.all_skills[intent].append(
            [wrapped_skill, params_regex, plugin_dir])

    def add_active_skill(self, skill_event):
        if skill_event.context.__class__ not in self.active_contexts.keys():
            self.active_contexts[skill_event.context.__class__] = []

        self.active_contexts[skill_event.context.__class__].append(
            skill_event.id)
        self.active_skills[skill_event.id] = skill_event
        GLOBAL_EMITTER.emit(EVENT_ON_SKILL_START, skill_event.id)

    def end_active_skill(self, skill_event):
        if self.has_active_skill(skill_event.id):
            if skill_event.context.__class__ in self.active_contexts.keys():
                self.active_contexts[skill_event.context.__class__].remove(
                    skill_event.id)

                if len(self.active_contexts[skill_event.context.__class__]) == 0:
                    del self.active_contexts[skill_event.context.__class__]

            del self.active_skills[skill_event.id]
            GLOBAL_EMITTER.emit(EVENT_ON_SKILL_END, skill_event.id)

    def get_skills_for_intent(self, intent):
        return self.all_skills.get(intent, [])

    def has_intent(self, intent):
        return intent in self.all_skills.keys()

    def has_active_skill(self, skill_id):
        return skill_id in self.active_skills.keys()

    def can_start_skills_in_context(self, context):
        return context not in self.active_contexts.keys()


SKILL_MANAGER = SkillManager()


def Skill(intents=[], params_regex=r".*"):
    """Decorate A Skill Method."""

    def inner(func):

        abs_path = os.path.abspath((inspect.stack()[1])[1])
        plugin_base_dir = re.match(
            r"(.*plugins[\\\/].*?)[\\\/]", abs_path).groups()[0]

        async def wrapper(event, args: list):

            SKILL_MANAGER.add_active_skill(event)

            try:
                await func(event, args)
            except Exception as e:
                log('Error while executing skill for intents |', intents)
                log(traceback.format_exc())

            SKILL_MANAGER.end_active_skill(event)

        for intent in intents:
            SKILL_MANAGER.add_skill(
                intent, wrapper, params_regex, plugin_base_dir)

        return wrapper

    return inner


def ServerHandler(route: str):
    def inner(handler):
        log('Added Route', route, handler)
        server = get_singleton(SINGLETON_SERVER_ID)
        server.app.default_router.add_rules([
            (route, handler),
        ])
        return handler

    return inner
