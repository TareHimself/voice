import json
import queue
import threading
from threading import Thread
from typing import Callable
import uuid

from events import EventEmitter

thread_queue = {}


# Use 'use' instead of 'run'
class ThreadEmitter(Thread):

    def __init__(self):
        super(ThreadEmitter, self).__init__(group=None, daemon=True)
        self.id = uuid.uuid1()
        thread_queue[self.id] = queue.Queue()

    def AddJob(self, job: str, *args, **kwargs):
        thread_queue[self.id].put({"j": job, "a": args, "k": kwargs})

    def ProcessJobs(self):
        job = thread_queue[self.id].get()
        if job:
            self.HandleJob(job['j'], *job['a'], **job['k'])

    def HandleJob(self, job:str, *args, **kwargs):
        pass

    def run(self):
        while True:
            self.ProcessJobs()


