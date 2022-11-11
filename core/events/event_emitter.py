from typing import Callable


class EventEmitter:
    def __init__(self):
        self.events = {}
        self.one_time_events = {}

    def on(self, event: str, callback: Callable[[], None]):
        if event not in self.events:
            self.events[event] = []
        self.events[event].append(callback)

    def once(self, event: str, callback: Callable[[], None]):
        if event not in self.events:
            self.one_time_events[event] = []
        self.one_time_events[event].append(callback)

    def off(self, event: str, callback: Callable[[], None]):
        if event in self.events and len(self.events[event]) > 0:
            self.events[event].remove(callback)

        if event in self.one_time_events and len(self.one_time_events[event]) > 0:
            self.one_time_events[event].remove(callback)

    def emit(self, event: str, *args, **kwargs):
        if event in self.events and len(self.events[event]) > 0:
            for callback in self.events[event]:
                callback(*args, **kwargs)

        if event in self.one_time_events and len(self.one_time_events[event]) > 0:
            for callback in self.one_time_events[event]:
                callback(*args, **kwargs)

            del self.one_time_events[event]
