from core.events import gEmitter
from core.skills import Skill


@Skill(["skill_self_maximize"])
async def MaximizeWindow(phrase, args):
    gEmitter.emit('window_action', "maximize")


@Skill(["skill_self_minimize"])
async def MinimizeWindow(phrase, args):
    gEmitter.emit('window_action', "minimize")


@Skill(["skill_self_restore"])
async def RestoreWindow(phrase, args):
    gEmitter.emit('window_action', "restore")
