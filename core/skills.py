import inspect
from os import path, getcwd, listdir
import traceback
from core.constants import NLU_PATH, DATA_PATH
from core.utils import GetNluData, StartSkill, EndSkill, TextToSpeech
import re

all_skills = {}
params_extractors = {}

hot_reloading = {}


def Skill(intents=[], params_regex=r".*"):
    filename = inspect.stack()[1].filename
    if filename not in hot_reloading.keys():
        hot_reloading[filename] = []

    def inner(func):
        async def wrapper(*args, **kwargs):
            StartSkill()
            try:
                await func(*args, **kwargs)
            except Exception as e:
                print('Error while executing skill for intents |', intents)
                print(traceback.format_exc())

            EndSkill()

        for intent in intents:
            all_skills[intent] = wrapper
            params_extractors[intent] = params_regex

        return wrapper

    hot_reloading[filename] = hot_reloading[filename] + [inner]

    return inner


def EntitiesToDict(e):
    result = {}
    for ent in e:
        result[ent['entity']] = ent['value']

    return result


async def TryRunCommand(phrase):
    try:
        parsed = await GetNluData(phrase)

        if not parsed:
            await TextToSpeech("I cannot answer that yet.", True)
            return

        intent, confidence = parsed
        if confidence >= 0.89 and intent in all_skills.keys():
            reg = params_extractors[intent]
            match = re.match(reg, phrase, re.IGNORECASE)
            print(match, reg)
            if match:
                await all_skills[intent](phrase, match.groups())
                return

        await TextToSpeech("I cannot answer that yet.", True)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
    return
