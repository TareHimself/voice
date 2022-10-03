import datetime

from word2number import w2n
from skills import Skill
from threads.scheduled_event import ScheduledEvent
from utils import EndSkill, TextToSpeech


@Skill("skill_schedule_add")
async def ScheduleEvent(phrase, entities):

    msg = entities[0]
    """
    end_time = datetime.datetime.utcnow()
    op = entities[2].strip().lower()
    if op == 'tomorrow':
        end_time = end_time + datetime.timedelta(days=1)
    elif op == 'an' or op == 'a':
        time_type = entities[3].lower()[:-1] if entities[3].endswith('s') else entities[3].lower()
        match time_type:
            case 'day':
                end_time = end_time + datetime.timedelta(days=1)
            case 'hour':
                end_time = end_time + datetime.timedelta(hours=1)
            case 'minute':
                end_time = end_time + datetime.timedelta(minutes=1)
            case 'second':
                end_time = end_time + datetime.timedelta(seconds=1)
    elif op == 'at':
        diff_hours = w2n.word_to_num(entities[3])
        diff_minutes = 0
        if len(entities) > 3:
            try:
                diff_minutes = w2n.word_to_num(entities[4])
            except ValueError as e:
                print(e)

        now = datetime.datetime.now()
        now.hour = diff_hours
        now.minute = diff_minutes
        end_time = now.astimezone()
    else:
        diff = w2n.word_to_num(entities[2])
        time_type = entities[3].lower()[:-1] if entities[3].endswith('s') else entities[3].lower()
        match time_type:
            case 'day':
                end_time = end_time + datetime.timedelta(days=diff)
            case 'hour':
                end_time = end_time + datetime.timedelta(hours=diff)
            case 'minute':
                end_time = end_time + datetime.timedelta(minutes=diff)
            case 'second':
                end_time = end_time + datetime.timedelta(seconds=diff)

    ScheduledEvent({'end_at': end_time, "msg": msg.strip()})
    TextToSpeech('Reminder added.')
    EndCommand()
    """
