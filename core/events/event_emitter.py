from typing import Callable


class EventEmitter:
    def __init__(self):
        self.events = {}

    def on(self, event: str, callback: Callable[[], None]):
        if event not in self.events:
            self.events[event] = []
        self.events[event].append(callback)

    def off(self, event: str, callback: Callable[[], None]):
        if event in self.events and len(self.events[event]) > 0:
            self.events[event].remove(callback)

    def emit(self, event: str, *args, **kwargs):
        if event in self.events and len(self.events[event]) > 0:
            for event in self.events[event]:
                event(*args, **kwargs)
