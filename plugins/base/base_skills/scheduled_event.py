import asyncio
import datetime
import time
from core.notifications import SendNotification
from datetime import datetime
from core.events import ThreadEmitter


class ScheduledEvent(ThreadEmitter):

    def __init__(self, event, timezone):
        super(ScheduledEvent, self).__init__()
        self.event = event
        self.tz = timezone
        self.start()

    async def runAsync(self):
        self.id = self.event['id']
        time.sleep((self.event['end_at'] -
                   datetime.now(self.tz)).total_seconds())

        SendNotification("Reminder", self.event['msg'])

    def run(self):
        asyncio.run(self.runAsync())
