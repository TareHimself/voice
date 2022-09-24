from events import global_emitter
from skills import Skill
from utils import TextToSpeech, EndCommand


@Skill(r"^(?:repeat|say|speak|voice)[\s]+(.+)")
def DisplayTime(phrase, keywords):
    TextToSpeech(keywords[0] + '.')
    EndCommand()
