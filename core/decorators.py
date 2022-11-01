import traceback
import uuid

from core.singletons import GetSingleton, Singleton,SetSingleton


class MainLoader(Singleton):
    def __init__(self):
        super().__init__(id="main-loader")
        self.loaders = {}

    def AddLoader(self, id, loader):
        if id not in self.loaders.keys():
            self.loaders.keys(id, loader)

    async def LoadAll(self, va):
        for loader in self.loaders.values():
            await loader()


main_loader = MainLoader()


def Loader(loader_id="{}".format(uuid.uuid4())):
    def inner(func):
        main_loader.AddLoader(loader_id, func)
        return func

    return inner


loaded_skills = {}
SetSingleton('skills',loaded_skills)


def Skill(intents=[], params_regex=r".*"):
    # filename = inspect.stack()[1].filename
    # if filename not in hot_reloading.keys():
    #     hot_reloading[filename] = []

    def inner(func):
        async def wrapper(*args, **kwargs):
            va = GetSingleton('assistant')
            va.OnSkillStart()
            try:
                await func(*tuple([va] + list(args)), **kwargs)
            except Exception as e:
                print('Error while executing skill for intents |', intents)
                print(traceback.format_exc())

            va.OnSkillEnd()

        for intent in intents:
            loaded_skills[intent] = [wrapper,params_regex]

        return wrapper

    return inner
