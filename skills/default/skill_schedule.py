import asyncio
from uuid import uuid4
from core.numwrd import num2wrd
from core.decorators import Skill
from datetime import datetime
from scheduled_event import ScheduledEvent
from core.utils import GetFollowUp, GetNluData, TextToSpeech
from core.str2time import stringToTime
from core.db import db
from core.constants import dynamic as data
from core.decorators import AssistantLoader
from core.logger import log
from default_utils import TimeToSttText


@AssistantLoader
async def Intialize():
    log('Generating Schedules Database')
    cur = db.cursor()
    cur.execute('''
            CREATE TABLE IF NOT EXISTS skill_schedule(
                id TEXT PRIMARY KEY,
                msg TEXT NOT NULL,
                end_at TEXT NOT NULL
            ) WITHOUT ROWID
            ''')

    for event in cur.execute("SELECT * FROM skill_schedule").fetchall():
        [event_id, msg, time] = list(event)
        time = datetime.fromisoformat(time)

        if time > datetime.now(data.timezone):
            ScheduledEvent({'end_at': time, "msg": msg, "id": event_id})
        else:
            cur.execute("DELETE FROM skill_schedule WHERE id=?", [event_id])

    db.commit()

    log('Done Generating Schedules Database')


@Skill(["skill_schedule_add"], r"(?:remind (?:me (?:to )))?([a-zA-Z ]+?)(?:\sin(?: a| an)?|\sat)\s(.*)")
async def ScheduleEvent(e, args):

    task, time = args
    end_time = stringToTime(time, data.timezone)

    if end_time:
        event_id = str(uuid4())
        cur = db.cursor()
        cur.execute('INSERT INTO skill_schedule VALUES(?, ?, ?)',
                    [event_id, task, end_time.isoformat()])

        db.commit()

        ScheduledEvent({'end_at': end_time, "msg": task, "id": event_id})

        TextToSpeech('Reminder added.')
    else:
        TextToSpeech('I am unable to parse the time.')


@Skill(["skill_schedule_list"])
async def ListSchedule(e, args):
    items = db.execute("SELECT * FROM skill_schedule").fetchall()
    await TextToSpeech('You have {} items scheduled  .'.format(num2wrd(len(items))), True)
    await asyncio.sleep(1)
    if len(items) > 0:
        await TextToSpeech('Would you like me to list them ?.', True)
        answer = await GetFollowUp(10)
        if answer:
            nlu_response = await GetNluData(answer)
            if nlu_response:
                intent, confidence = nlu_response
                if intent == "skill_affirm":
                    for i in range(len(items)):
                        await TextToSpeech('{}. {}. At {}.'.format(num2wrd(i + 1), items[i][1], TimeToSttText(datetime.fromisoformat(items[i][2]))), True)
