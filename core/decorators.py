import traceback
import uuid
import inspect
from functools import partial, wraps
from core.logger import log
from core.singletons import GetSingleton, Singleton, SetSingleton


class MainLoader(Singleton):
    def __init__(self):
        super().__init__(id="main-loader")
        self.loaders = {}

    def __len__(self):
        return len(self.loaders.values())

    def AddLoader(self, id, loader):
        if id not in self.loaders.keys():
            self.loaders[id] = loader

    async def LoadCurrent(self, va):

        items = list(self.loaders.keys())
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


def AssistantLoader(f, loader_id=""):
    loader_id = loader_id if len(
        loader_id) > 0 else "unnamed-{}".format(uuid.uuid4())
    log("Adding loader", loader_id)
    main_loader.AddLoader(loader_id, f)
    return f


loaded_skills = {}
SetSingleton('skills', loaded_skills)


def Skill(intents=[], params_regex=r".*"):
    # filename = inspect.stack()[1].filename
    # if filename not in hot_reloading.keys():
    #     hot_reloading[filename] = []

    def inner(func):
        async def wrapper(event, args):
            va = GetSingleton('assistant')
            va.OnSkillStart()
            try:
                await func(*tuple([] + list(args)), **kwargs)
            except Exception as e:
                log('Error while executing skill for intents |', intents)
                log(traceback.format_exc())

            va.OnSkillEnd()

        for intent in intents:
            loaded_skills[intent] = [wrapper, params_regex]

        return wrapper

    return inner
