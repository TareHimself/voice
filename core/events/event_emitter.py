from typing import Callable
import asyncio
from core.loops import create_async_loop
emitter_loop = create_async_loop()

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
                possible_corutine = callback(*args, **kwargs)
                if possible_corutine and asyncio.iscoroutine(possible_corutine):
                    asyncio.run_coroutine_threadsafe(possible_corutine,emitter_loop)

        if event in self.one_time_events and len(self.one_time_events[event]) > 0:
            for callback in self.one_time_events[event]:
                possible_corutine = callback(*args, **kwargs)
                if possible_corutine and asyncio.iscoroutine(possible_corutine):
                    asyncio.run_coroutine_threadsafe(
                        possible_corutine, emitter_loop)

            del self.one_time_events[event]
