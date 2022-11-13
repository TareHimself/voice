from core.decorators import Skill
from plugins.base.text_to_speech import text_to_speech
from core.assistant import SkillEvent


@Skill(["skill_self_say"], r"(?:(?:say|speak)\s?)?(.*)")
async def speak(e: SkillEvent, args: list):
    text_to_speech(args[0] + '.')
