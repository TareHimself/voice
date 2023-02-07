import pathlib
from os import path
import json
import random
import core
from core.assistant import SkillEvent
from core.decorators import Skill
from plugins.base.constants import PLUGIN_ID

LOADER_PATH = pathlib.Path(__file__).parent.resolve()
INTENTS_PATH = path.normpath(path.join(LOADER_PATH, 'intents.json'))


class ConversationalPlugin(core.assistant.AssistantPlugin):
    def __init__(self, assistant: core.assistant.Assistant):
        super(ConversationalPlugin, self).__init__(assistant)

        with open(path.normpath(path.join(LOADER_PATH, 'intents.json')), 'r') as f:
            self.intents = json.load(f)['tags']

    def get_intents(self):
        return self.intents

    def get_info(self):
        return {
            "id": "Test Conversation Plugin",
            "author": "Oyintare Ebelo"
        }


def get_plugin():
    return ConversationalPlugin


@Skill(["skill_hello"])
async def do_math(e: SkillEvent, args: list):
    await e.context.handle_response(random.choice(e.plugin.get_intents()[0]['responses']))


@Skill(["skill_insult"])
async def do_math(e: SkillEvent, args: list):
    global intents
    await e.context.handle_response(random.choice(e.plugin.get_intents()[1]['responses']))
