import inspect
from os import path, getcwd, listdir
import traceback
from core.constants_1 import NLU_PATH, DATA_PATH
from core.utils import GetNluData, StartSkill, EndSkill, TextToSpeech
import re


hot_reloading = {}


async def TryRunCommand(phrase):
    pass
