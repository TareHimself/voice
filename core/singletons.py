
all_singletons = {}


def GetSingleton(id: str):
    return all_singletons.get(id)


def GetSingletons():
    return all_singletons


def SetSingleton(id: str, object):
    all_singletons[id] = object


class Singleton:
    def __init__(self, id) -> None:
        self.id = id
        SetSingleton(id, self)
