import datetime
import time
from notifypy.notify import Notify
from events import global_emitter
from events.thread_emitter import ThreadEmitter

active_timers = {}


class Timer(ThreadEmitter):

    def __init__(self,timer_id, length=0, callback=lambda: None, loop=False):
        super(Timer, self).__init__(emitter_id=timer_id)
        self.callback = callback
        self.length = length
        self.loop = loop
        self.start()

    def run(self):

        if self.loop:
            while active_timers[self.id]:
                time.sleep(self.length)
                if active_timers[self.id]:
                    self.callback()
        else:
            time.sleep(self.length)
            if active_timers[self.id]:
                self.callback()

        del active_timers[self.id]


def StopTimer(timer_id):
    if timer_id in active_timers.keys():
        active_timers[id] = False


def StartTimer(timer_id, length=0, callback=lambda: None, loop=False):
    active_timers[timer_id] = True
    Timer(timer_id=timer_id, length=length, callback=callback, loop=loop)
