from events import global_emitter
from skills import RegisterSkill, skill


@skill(r"^(repeat|say|speak|voice)[\s]+(.+)")
def DisplayTime(phrase, match):
    global_emitter.emit('do_speech', match[0][1] + '.')