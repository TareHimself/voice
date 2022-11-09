import queue
import threading

import uuid
lock = threading.Lock()


class CoreThread(threading.Thread):

    def __init__(self):
        super().__init__(group=None, daemon=True)

    def print(self, *args, **kwargs):
        print(*args, **kwargs)

    def run(self):
        pass
