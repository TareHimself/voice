import datetime

from word2number import w2n
from notifypy import Notify
from skills import Skill
from threads.scheduled_event import ScheduledEvent
from utils import EndCommand


@Skill(r"^(?:remind me to |remind me |remind )(.*)(?:(tomorrow)|in (.*) (hours?)|in (.*) (minutes?)|in (.*) ("
       r"seconds?)|at (.*))")
def ScheduleEvent(phrase, keywords):

    msg = keywords[0]
    end_time = datetime.datetime.utcnow()
    op = keywords[0].strip().lower()
    if op == 'tomorrow':
        end_time += + datetime.timedelta(days=1)
    elif op == 'an' or op == 'a':
        time_type = keywords[2].lower()[:-1] if keywords[2].endswith('s') else keywords[2].lower()
        match time_type:
            case 'hour':
                end_time += + datetime.timedelta(hours=1)
            case 'minute':
                end_time += + datetime.timedelta(minutes=1)
            case 'second':
                end_time += + datetime.timedelta(seconds=1)
    elif op == 'at':
        pass
    else:
        diff = w2n.word_to_num(keywords[1])
        time_type = keywords[2].lower()[:-1] if keywords[2].endswith('s') else keywords[2].lower()
        match time_type:
            case 'hour':
                end_time += + datetime.timedelta(hours=diff)
            case 'minute':
                end_time += + datetime.timedelta(minutes=diff)
            case 'second':
                end_time += + datetime.timedelta(seconds=diff)

    ScheduledEvent({'end_at': end_time, "msg":""})
    EndCommand()
