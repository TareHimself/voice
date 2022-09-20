from events import global_emitter
from skills import RegisterSkill


def Pause(phrase, match):
    pass

def Resume(phrase, match):
    pass

def Skip(phrase, match):
    pass

def Play(phrase, match):
    pass


RegisterSkill(Pause, r"^pause spotify$")

RegisterSkill(Resume, r"^resume spotify$")

RegisterSkill(Skip, r"^skip spotify$")

RegisterSkill(Play, r"^(play)[\s]+(.+)[\s]+(on spotify)$")