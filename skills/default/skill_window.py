from core.events import global_emitter
from core.skills import Skill


@Skill(["skill_self_maximize"])
async def MaximizeWindow(phrase, args):
    global_emitter.emit('window_action', "maximize")

@Skill(["skill_self_minimize"])
async def MinimizeWindow(phrase, args):
    global_emitter.emit('window_action', "minimize")


@Skill(["skill_self_restore"])
async def RestoreWindow(phrase, args):
    global_emitter.emit('window_action', "restore")
