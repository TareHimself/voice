
all_singletons = {}


def get_singleton(id: str):
    return all_singletons.get(id)


def get_singletons():
    return all_singletons


def set_singleton(id: str, object):
    all_singletons[id] = object


class Singleton:
    def __init__(self, id) -> None:
        self.id = id
        set_singleton(id, self)
