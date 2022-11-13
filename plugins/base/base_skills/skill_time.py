from datetime import datetime, timezone
import random
from core.decorators import Skill
from core.assistant import SkillEvent
from plugins.base.text_to_speech import text_to_speech
from .utils import time_to_stt_text


@Skill(["skill_time"])
async def display_time(e: SkillEvent, args: list):
    current_time = datetime.now(timezone.utc).astimezone()
    time_to_say = random.choice(['The time is {}.', "It's {}.", "Right now it's {}."]).format(
        current_time.strftime(f'%I:%M {"AM" if current_time.hour < 12 else "PM"}'))

    await e.context.handle_response(time_to_say)
