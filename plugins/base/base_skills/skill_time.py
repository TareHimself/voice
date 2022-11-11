from datetime import datetime, timezone
import random
from core.decorators import Skill
from core.assistant import SkillEvent
from plugins.base.text_to_speech import TextToSpeech
from .utils import TimeToSttText


@Skill(["skill_time"])
async def DisplayTime(e: SkillEvent, args):
    current_time = datetime.now(timezone.utc).astimezone()
    time_to_say = random.choice(['The time is {}.', "It's {}.", "Right now it's {}."]).format(
        TimeToSttText(current_time))

    TextToSpeech(time_to_say)
