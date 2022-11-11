import traceback
import uuid
import inspect
from core.constants import SINGLETON_SERVER_ID, SINGLETON_MAIN_LOADER_ID,SINGLETON_ASSISTANT_ID
from core.logger import log
from core.singletons import GetSingleton, Singleton, SetSingleton


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


main_loader = MainLoader()


def AssistantLoader(loader_id=""):

    if callable(loader_id):
        main_loader.AddLoader("loader-{}".format(uuid.uuid4()), loader_id)
        return loader_id

    def wrapper(func):
        nonlocal loader_id
        main_loader.AddLoader(loader_id, func)
        return func
    return wrapper


loaded_skills = {}
SetSingleton('skills', loaded_skills)


def Skill(intents=[], params_regex=r".*"):

    # filename = inspect.stack()[1].filename
    # if filename not in hot_reloading.keys():
    #     hot_reloading[filename] = []

    def inner(func):
        async def wrapper(event, args):
            va = GetSingleton(SINGLETON_ASSISTANT_ID)
            va.OnSkillStart()
            try:
                await func(event, args)
            except Exception as e:
                log('Error while executing skill for intents |', intents)
                log(traceback.format_exc())

            va.OnSkillEnd()

        for intent in intents:
            loaded_skills[intent] = [wrapper, params_regex]

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
