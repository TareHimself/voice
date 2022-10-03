from datetime import  datetime, timezone
from skill_dev import  Skill
from num2words import num2words

from core.utils import TextToSpeech


@Skill("skill_time")
async def DisplayTime(phrase, entities):
    current_time = datetime.now(timezone.utc).astimezone()
    time_to_say = 'The time is '

    for word in (current_time.strftime('%I %M') + (" ai em." if current_time.hour < 12 else " pea em.")).split():
        if word.isdigit():
            time_to_say += num2words(int(word)) + " "
        else:
            time_to_say += word + " "

    TextToSpeech(time_to_say)