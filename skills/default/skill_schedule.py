from core.skills import Skill
from parsedatetime import Calendar
from pytz import timezone
from core.threads import ScheduledEvent
from core.utils import TextToSpeech
cal = Calendar()
tz = timezone("US/Eastern")
@Skill("skill_schedule_add")
async def ScheduleEvent(phrase, entities):

    if 'time' in entities.keys() and 'schedule_task' in entities.keys():
        end_time = cal.parseDT(datetimeString=entities['time'], tzinfo=tz)[0]

        ScheduledEvent({'end_at': end_time, "msg": entities['schedule_task']})

        TextToSpeech('Reminder added.')
