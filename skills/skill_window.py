from datetime import datetime, timezone
from events import global_emitter
from skills import Skill
from utils import EndCommand


@Skill(r"^(maximize|maximize (?:window|your window))$")
def MaximizeWindow(phrase, keywords):
    global_emitter.emit('window_action', "maximize")
    EndCommand()


@Skill(r"^(minimize|minimize (?:window|your window))$")
def MinimizeWindow(phrase, keywords):
    global_emitter.emit('window_action', "minimize")
    EndCommand()


@Skill(r"^(restore|restore (?:window|your window))$")
def RestoreWindow(phrase, keywords):
    global_emitter.emit('window_action', "restore")
    EndCommand()
