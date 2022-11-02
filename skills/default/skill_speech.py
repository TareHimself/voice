from core.decorators import Skill
from core.utils import TextToSpeech


@Skill(["skill_self_say"], r"(?:(?:say|speak)\s?)?(.*)")
async def Speak(e, args):
    TextToSpeech(args[0] + '.')
