from datetime import datetime, timezone
import random
from core.decorators import Skill
from core.numwrd import num2wrd
from core.utils import TextToSpeech
from default_utils import TimeToSttText


@Skill(["skill_time"])
async def DisplayTime(e, args):
    current_time = datetime.now(timezone.utc).astimezone()
    time_to_say = random.choice(['The time is {}.', "It's {}.", "Right now it's {}."]).format(
        TimeToSttText(current_time))

    TextToSpeech(time_to_say)