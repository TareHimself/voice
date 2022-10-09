import asyncio
import datetime
import time
from notifypy.notify import Notify
from datetime import datetime
from pytz import timezone
from core.events import ThreadEmitter,global_emitter
tz = timezone("US/Eastern")

class ScheduledEvent(ThreadEmitter):

    def __init__(self, event):
        super(ScheduledEvent, self).__init__()
        self.event = event
        self.start()

    async def runAsync(self):
        print("starting timer for event: ", self.event['msg'])
        print(self.event['end_at'],datetime.now(tz))
        time.sleep((self.event['end_at'] - datetime.now(tz)).total_seconds())

        notification = Notify()
        notification.application_name = "Voice Assistant"
        notification.title = "Reminder"
        notification.message = self.event['msg']
        notification.send()
    
    def run(self):
        asyncio.run(self.runAsync())
