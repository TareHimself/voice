import datetime
import time
from notifypy.notify import Notify
from core.events.thread_emitter import ThreadEmitter


class ScheduledEvent(ThreadEmitter):

    def __init__(self, event):
        super(ScheduledEvent, self).__init__()
        self.event = event
        self.start()

    def run(self):
        print("starting timer for event: ", self.event['msg'])
        time.sleep((self.event['end_at'] - datetime.datetime.utcnow()).total_seconds())

        notification = Notify()
        notification.title = "Reminder"
        notification.message = self.event['msg']
        notification.send()
