import asyncio
import datetime
import time
from core.notifications import SendNotification
from datetime import datetime
from core.events import ThreadEmitter
from core.constants import dynamic as data


class ScheduledEvent(ThreadEmitter):

    def __init__(self, event):
        super(ScheduledEvent, self).__init__()
        self.event = event
        self.start()

    async def runAsync(self):
        self.id = self.event['id']
        time.sleep((self.event['end_at'] -
                   datetime.now(data.timezone)).total_seconds())

        SendNotification("Reminder", self.event['msg'])

    def run(self):
        asyncio.run(self.runAsync())
