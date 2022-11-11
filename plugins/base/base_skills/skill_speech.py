from core.decorators import Skill
from plugins.base.text_to_speech import TextToSpeech
from core.assistant import SkillEvent

@Skill(["skill_self_say"], r"(?:(?:say|speak)\s?)?(.*)")
async def Speak(e: SkillEvent, args):
    TextToSpeech(args[0] + '.')
