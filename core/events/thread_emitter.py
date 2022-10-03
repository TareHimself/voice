import queue
import threading
from threading import Thread
import uuid

thread_queue = {}

lock = threading.Lock()


# Use 'use' instead of 'run'
class ThreadEmitter(Thread):

    def __init__(self, use_blocking_queue=True, emitter_id=None):
        super(ThreadEmitter, self).__init__(group=None, daemon=True)
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

    def AquireLock(self):
        lock.acquire()

    def ReleaseLock(self):
        lock.release()

    def run(self):
        while True:
            self.ProcessJobs()
