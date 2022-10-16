from core.skills import Skill
from core.utils import TextToSpeech


@Skill(["skill_self_say"],r"(?:(?:say|speak)\s?)?(.*)")
async def Speak(phrase, args):
    TextToSpeech(args[0] + '.')
    
