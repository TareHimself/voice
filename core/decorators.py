import traceback
import uuid
import inspect
from core.constants import SINGLETON_SERVER_ID, SINGLETON_MAIN_LOADER_ID, SINGLETON_SKILL_MANAGER_ID, \
    EVENT_ON_SKILL_START, EVENT_ON_SKILL_END
from core.logger import log
from core.singletons import GetSingleton, Singleton, SetSingleton
from core.events import gEmitter


class MainLoader(Singleton):
    def __init__(self):
        super().__init__(id=SINGLETON_MAIN_LOADER_ID)
        self.loaders = {}

    def __len__(self):
        return len(self.loaders.values())

    def AddLoader(self, id, loader):
        if id not in self.loaders.keys():
            self.loaders[id] = loader

    async def LoadCurrent(self, va):
        items = list(self.loaders.keys())
        log(f"About to load {items}")
        try:
            for id in items:
                call_funct = self.loaders[id]
                if len(inspect.getargspec(call_funct).args) == 0:
                    await call_funct()
                else:
                    await call_funct(va)
                del self.loaders[id]

            if len(self.loaders.keys()):
                await self.LoadCurrent(va)
        except Exception as e:
            log(e)


MAIN_LOADER = MainLoader()


def AssistantLoader(loader_id=""):
    if callable(loader_id):
        MAIN_LOADER.AddLoader("loader-{}".format(uuid.uuid4()), loader_id)
        return loader_id

    def wrapper(func):
        nonlocal loader_id
        MAIN_LOADER.AddLoader(loader_id, func)
        return func

    return wrapper




class SkillManager(Singleton):
    def __init__(self):
        super().__init__(id=SINGLETON_SKILL_MANAGER_ID)
        self.all_skills = {}
        self.active_skills = {}
        gEmitter.on(EVENT_ON_SKILL_END, self.OnSkillEnd)

    def AddSkill(self, intent, wrapped_skill, params_regex):
        if not self.HasIntent(intent):
            self.all_skills[intent] = []
        self.all_skills[intent].append([wrapped_skill, params_regex])

    def AddActiveSkill(self, skill_event):
        self.active_skills[skill_event.id] = skill_event

    def OnSkillEnd(self, skill_id):
        if self.HasActiveSkill(skill_id):
            del self.active_skills[skill_id]

    def GetSkillsForIntent(self, intent):
        return self.all_skills.get(intent, [])

    def HasIntent(self,intent):
        return intent in self.all_skills.keys()

    def HasActiveSkill(self,skill_id):
        return skill_id in self.active_skills.keys()



SKILL_MANAGER = SkillManager()


def Skill(intents=[], params_regex=r".*"):
    # filename = inspect.stack()[1].filename
    # if filename not in hot_reloading.keys():
    #     hot_reloading[filename] = []

    def inner(func):
        async def wrapper(event, args):

            log('WRAPPER CALLED')

            SKILL_MANAGER.AddActiveSkill(event)

            gEmitter.emit(EVENT_ON_SKILL_START, event.id)

            try:
                await func(event, args)
            except Exception as e:
                log('Error while executing skill for intents |', intents)
                log(traceback.format_exc())

            gEmitter.emit(EVENT_ON_SKILL_END, event.id)

        for intent in intents:
            SKILL_MANAGER.AddSkill(intent, wrapper, params_regex)

        return wrapper

    return inner


def ServerHandler(route: str):
    def inner(handler):
        log('Added Route', route, handler)
        server = GetSingleton(SINGLETON_SERVER_ID)
        server.app.default_router.add_rules([
            (route, handler),
        ])
        return handler

    return inner
