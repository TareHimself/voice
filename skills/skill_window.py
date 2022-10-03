from events import global_emitter
from skills import Skill


@Skill("skill_self_maximize")
async def MaximizeWindow(phrase, entities):
    global_emitter.emit('window_action', "maximize")


@Skill("skill_self_minimize")
async def MinimizeWindow(phrase, entities):
    global_emitter.emit('window_action', "minimize")


@Skill("skill_self_restore")
async def RestoreWindow(phrase, entities):
    global_emitter.emit('window_action', "restore")
