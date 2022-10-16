import asyncio
import datetime
import time
from core.notifications import SendNotification
from datetime import datetime
from pytz import timezone
from core.events import ThreadEmitter
tz = timezone("US/Eastern")


class ScheduledEvent(ThreadEmitter):

    def __init__(self, event):
        super(ScheduledEvent, self).__init__()
        self.event = event
        self.start()

    async def runAsync(self):
        print("starting timer for event: ", self.event['msg'])
        print(self.event['end_at'], datetime.now(tz))
        time.sleep((self.event['end_at'] - datetime.now(tz)).total_seconds())

        SendNotification("Reminder", self.event['msg'])

    def run(self):
        asyncio.run(self.runAsync())
