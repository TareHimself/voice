import traceback
import uuid
import inspect
from core.constants import SINGLETON_SERVER_ID, SINGLETON_MAIN_LOADER_ID, SINGLETON_SKILL_MANAGER_ID, \
    EVENT_ON_SKILL_START, EVENT_ON_SKILL_END
from core.logger import log
from core.singletons import get_singleton, Singleton, set_singleton
from core.events import gEmitter


class MainLoader(Singleton):
    def __init__(self):
        super().__init__(id=SINGLETON_MAIN_LOADER_ID)
        self.loaders = {}

    def __len__(self):
        return len(self.loaders.values())

    def add_loader(self, id, loader):
        if id not in self.loaders.keys():
            self.loaders[id] = loader

    async def load_current(self, va):
        items = list(self.loaders.keys())
        log(f"About to load {items}")
        try:
            for id in items:
                call_funct = self.loaders[id]

                if len(inspect.signature(call_funct).parameters) == 0:
                    await call_funct()
                else:
                    await call_funct(va)
                del self.loaders[id]

            if len(self.loaders.keys()):
                await self.load_current(va)
        except Exception as e:
            log(e)


MAIN_LOADER = MainLoader()


def AssistantLoader(loader_id=""):
    if callable(loader_id):
        MAIN_LOADER.add_loader("loader-{}".format(uuid.uuid4()), loader_id)
        return loader_id

    def wrapper(func):
        nonlocal loader_id
        MAIN_LOADER.add_loader(loader_id, func)
        return func

    return wrapper


class SkillManager(Singleton):
    def __init__(self):
        super().__init__(id=SINGLETON_SKILL_MANAGER_ID)
        self.all_skills = {}
        self.active_skills = {}

    def add_skill(self, intent, wrapped_skill, params_regex):
        if not self.has_intent(intent):
            self.all_skills[intent] = []
        self.all_skills[intent].append([wrapped_skill, params_regex])

    def add_active_skill(self, skill_event):
        self.active_skills[skill_event.id] = skill_event
        gEmitter.emit(EVENT_ON_SKILL_START, skill_event.id)

    def end_active_skill(self, skill_id):
        if self.has_active_skill(skill_id):
            del self.active_skills[skill_id]
            gEmitter.emit(EVENT_ON_SKILL_START, skill_id)

    def get_skills_for_intent(self, intent):
        return self.all_skills.get(intent, [])

    def has_intent(self, intent):
        return intent in self.all_skills.keys()

    def has_active_skill(self, skill_id):
        return skill_id in self.active_skills.keys()


SKILL_MANAGER = SkillManager()


def Skill(intents=[], params_regex=r".*"):
    """Decorate A Skill Method."""

    def inner(func):
        async def wrapper(event, args: list):

            SKILL_MANAGER.add_active_skill(event)

            try:
                await func(event, args)
            except Exception as e:
                log('Error while executing skill for intents |', intents)
                log(traceback.format_exc())

            SKILL_MANAGER.end_active_skill(event.id)

        for intent in intents:
            SKILL_MANAGER.add_skill(intent, wrapper, params_regex)

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
