import pathlib
from os import path
import json
from plugins.base.constants import PLUGIN_ID

from plugins.base.base_skills import *
from plugins.base.speech_recognition import *
from plugins.base.text_to_speech import *

LOADER_PATH = pathlib.Path(__file__).parent.resolve()
INTENTS_PATH = path.normpath(path.join(LOADER_PATH, 'intents.json'))


def GetId():
    return PLUGIN_ID


def GetIntents():
    with open(INTENTS_PATH, 'r') as f:
        return json.load(f)['tags']
