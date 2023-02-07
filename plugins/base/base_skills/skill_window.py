from core.events import GLOBAL_EMITTER
from core.assistant import SkillEvent
from core.decorators import Skill


@Skill(["skill_self_maximize"])
async def maximize_window(e: SkillEvent, args: list):
    GLOBAL_EMITTER.emit('window_action', "maximize")


@Skill(["skill_self_minimize"])
async def minimize_window(e: SkillEvent, args: list):
    GLOBAL_EMITTER.emit('window_action', "minimize")


@Skill(["skill_self_restore"])
async def restore_window(e: SkillEvent, args: list):
    GLOBAL_EMITTER.emit('window_action', "restore")
