from datetime import datetime, timezone
from events import global_emitter
from skills import RegisterSkill


def MaximizeWindow(phrase, match):
    global_emitter.emit('window_action', "maximize")


def MinimizeWindow(phrase, match):
    global_emitter.emit('window_action', "minimize")


def RestoreWindow(phrase, match):
    global_emitter.emit('window_action', "restore")


RegisterSkill(MaximizeWindow, r"^(maximize|maximize (window|your window))$")

RegisterSkill(MinimizeWindow, r"^(minimize|minimize (window|your window))$")

RegisterSkill(RestoreWindow, r"^(restore|restore (window|your window))$")
