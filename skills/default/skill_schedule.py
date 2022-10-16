from ast import arg
from core.skills import Skill
from parsedatetime import Calendar
from pytz import timezone
from scheduled_event import ScheduledEvent
from core.utils import TextToSpeech
from str2time import stringToTime
cal = Calendar()
tz = timezone("US/Eastern")
@Skill(["skill_schedule_add"],r"(?:remind (?:me (?:to )))?([a-zA-Z ]+?)(?:\sin(?: a| an)?|\sat)\s(.*)")
async def ScheduleEvent(phrase, args):

    task , time = args
    print(args)
    end_time = stringToTime(time,tz)

    if end_time:
        ScheduledEvent({'end_at': end_time, "msg": task})
        print(task,end_time)
        TextToSpeech('Reminder added.')
    else:
        TextToSpeech('I am unable to parse the time.')
        

        
