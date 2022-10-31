import queue
import threading

import uuid
lock = threading.Lock()


class CoreThread(threading.Thread):

    def __init__(self):
        super().__init__(group=None, daemon=True)

    def _lock(self):
        lock.acquire()

    def _release(self):
        lock.release()

    def print(self, *args, **kwargs):
        self._lock()
        print(*args, **kwargs)
        self._release()

    def run(self):
        pass
