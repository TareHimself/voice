from core.skills import Skill
from core.utils import TextToSpeech


@Skill("skill_self_say")
async def Speak(phrase, entities):
    TextToSpeech(entities['speech_text'] + '.')
    
