import pathlib
from os import path
import json
from plugins.base.base_skills import *
from plugins.base.speech_recognition import *
from plugins.base.text_to_speech import *
import core

LOADER_PATH = pathlib.Path(__file__).parent.resolve()


class BasePlugin(core.assistant.AssistantPlugin):
    def __init__(self, assistant: 'Assistant'):
        super(BasePlugin, self).__init__(assistant)
        with open(path.normpath(path.join(LOADER_PATH, 'info.json')), 'r') as f:
            self.info = json.load(f)

        with open(path.normpath(path.join(LOADER_PATH, 'intents.json')), 'r') as f:
            self.intents = json.load(f)['tags']

    def get_intents(self):
        return self.intents

    def get_info(self):
        return self.info


def get_plugin():
    return BasePlugin
