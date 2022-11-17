import pathlib
from os import path
import json
import random

from core.assistant import SkillEvent
from core.decorators import Skill
from plugins.base.constants import PLUGIN_ID

LOADER_PATH = pathlib.Path(__file__).parent.resolve()
INTENTS_PATH = path.normpath(path.join(LOADER_PATH, 'intents.json'))

intents = []

def GetId():
    return PLUGIN_ID


def get_intents():
    global intents
    with open(INTENTS_PATH, 'r') as f:
        intents = json.load(f)['tags']
        return intents

@Skill(["skill_hello"])
async def do_math(e: SkillEvent, args: list):
    global intents
    await e.context.handle_response(random.choice(intents[0]['responses']))

@Skill(["skill_insult"])
async def do_math(e: SkillEvent, args: list):
    global intents
    await e.context.handle_response(random.choice(intents[1]['responses']))
