from core.events import gEmitter
from core.assistant import SkillEvent
from core.decorators import Skill


@Skill(["skill_self_maximize"])
async def MaximizeWindow(e: SkillEvent, args):
    gEmitter.emit('window_action', "maximize")


@Skill(["skill_self_minimize"])
async def MinimizeWindow(e: SkillEvent, args):
    gEmitter.emit('window_action', "minimize")


@Skill(["skill_self_restore"])
async def RestoreWindow(e: SkillEvent, args):
    gEmitter.emit('window_action', "restore")
