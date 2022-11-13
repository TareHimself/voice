import asyncio
from uuid import uuid4
from core.assistant import Assistant
from core.numwrd import num2wrd
from core.decorators import Skill
from datetime import datetime
from .scheduled_event import ScheduledEvent
from core.utils import parse_phrase
from core.assistant import SkillEvent
from core.strtime import string_to_time
from core.db import db
from core.decorators import AssistantLoader
from core.logger import log
from .utils import time_to_stt_text


@AssistantLoader
async def initialize(va: Assistant):
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

        if time > datetime.now(va.tz):
            ScheduledEvent({'end_at': time, "msg": msg, "id": event_id}, va.tz)
        else:
            cur.execute("DELETE FROM skill_schedule WHERE id=?", [event_id])

    db.commit()

    log('Done Generating Schedules Database')


@Skill(["skill_schedule_add"], r"(?:remind (?:me (?:to )))?([a-zA-Z ]+?)(?:\sin(?: a| an)?|\sat)\s(.*)")
async def schedule_event(e: SkillEvent, args: list):
    tz = e.assistant.tz
    task, time = args
    end_time = string_to_time(time, tz)

    if end_time:
        event_id = str(uuid4())
        cur = db.cursor()
        cur.execute('INSERT INTO skill_schedule VALUES(?, ?, ?)',
                    [event_id, task, end_time.isoformat()])

        db.commit()

        ScheduledEvent({'end_at': end_time, "msg": task,
                       "id": event_id}, tz)

        await e.context.handle_response('Reminder added.')
    else:
        await e.context.handle_response('I am unable to parse the time.')


@Skill(["skill_schedule_list"])
async def list_schedule(e: SkillEvent, args: list):
    items = db.execute("SELECT * FROM skill_schedule").fetchall()

    await e.context.handle_response('You have {} items scheduled.'.format(num2wrd(len(items))))
    await asyncio.sleep(1)
    if len(items) > 0:
        await e.context.handle_response('Would you like me to list them ?')

        answer = await e.context.get_followup(10)

        log("ANSWER FROM FOLLOWUP", answer)
        if answer:
            nlu_response = await parse_phrase(answer)
            if nlu_response:
                confidence, intent = nlu_response
                if intent == "skill_affirm":
                    for i in range(len(items)):
                        t = datetime.fromisoformat(items[i][2])
                        await e.context.handle_response('{}. {}, at {}.'.format(i + 1, items[i][1], t.strftime(f'%I:%M {"AM" if t.hour < 12 else "PM"}')))
                else:
                    await e.context.handle_response('Ok.')
