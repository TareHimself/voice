import queue
from .thread import CoreThread
import uuid

thread_queue = {}


# Use 'use' instead of 'run'
class ThreadEmitter(CoreThread):

    def __init__(self, use_blocking_queue=True, emitter_id=None):
        super().__init__()
        self.id = emitter_id if emitter_id else uuid.uuid1()
        thread_queue[self.id] = queue.Queue()

    def AddJob(self, job: str, *args, **kwargs):
        thread_queue[self.id].put({"j": job, "a": args, "k": kwargs})

    def ProcessJobs(self):
        job = thread_queue[self.id].get()
        if job:
            self.HandleJob(job['j'], *job['a'], **job['k'])

    def HandleJob(self, job: str, *args, **kwargs):
        pass

    def run(self):
        while True:
            self.ProcessJobs()
