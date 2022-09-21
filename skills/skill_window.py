from datetime import datetime, timezone
from events import global_emitter
from skills import RegisterSkill, skill


@skill(r"^(maximize|maximize (window|your window))$")

def MaximizeWindow(phrase, match):
    global_emitter.emit('window_action', "maximize")

@skill(r"^(minimize|minimize (window|your window))$")
def MinimizeWindow(phrase, match):
    global_emitter.emit('window_action', "minimize")


@skill(r"^(restore|restore (window|your window))$")
def RestoreWindow(phrase, match):
    global_emitter.emit('window_action', "restore")

