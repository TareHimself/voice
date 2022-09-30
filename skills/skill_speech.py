from events import global_emitter
from skills import Skill
from utils import TextToSpeech, EndCommand


@Skill("skill_self_say")
def Speak(phrase, keywords):
    TextToSpeech(keywords[0] + '.')
    EndCommand()
