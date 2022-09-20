from events import global_emitter
from skills import RegisterSkill


def DisplayTime(phrase, match):
    global_emitter.emit('do_speech', match[0][1] + '.')


RegisterSkill(DisplayTime, r"^(repeat|say|speak)[\s]+(.+)")