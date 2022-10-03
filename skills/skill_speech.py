from skills import Skill
from utils import TextToSpeech


@Skill("skill_self_say")
async def Speak(phrase, entities):
    TextToSpeech(entities['speech_text'] + '.')
    
