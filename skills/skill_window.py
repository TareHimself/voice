from datetime import datetime, timezone
from events import global_emitter
from skills import Skill
from utils import EndCommand


@Skill("skill_self_maximize")
def MaximizeWindow(phrase, keywords):
    global_emitter.emit('window_action', "maximize")
    EndCommand()


@Skill("skill_self_minimize")
def MinimizeWindow(phrase, keywords):
    global_emitter.emit('window_action', "minimize")
    EndCommand()


@Skill("skill_self_restore")
def RestoreWindow(phrase, keywords):
    global_emitter.emit('window_action', "restore")
    EndCommand()
