from core.decorators import Skill
from plugins.base.text_to_speech import TextToSpeech


@Skill(["skill_self_say"], r"(?:(?:say|speak)\s?)?(.*)")
async def Speak(e, args):
    TextToSpeech(args[0] + '.')
