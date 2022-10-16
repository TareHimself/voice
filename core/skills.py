from os import path, getcwd, listdir
import traceback
from core.constants import NLU_PATH, DATA_PATH
from core.utils import GetNluData, StartSkill, EndSkill, TextToSpeech
import re
all_skills = {}
params_extractors = {}


def Skill(intents=[],params_regex=r".*"):
    def inner(func):
        async def wrapper(*args, **kwargs):
            StartSkill()
            try:
                await func(*args, **kwargs)
            except Exception as e:
                print('Error while executing skill for intents |',intents)
                print(traceback.format_exc())
            
            EndSkill()

        for intent in intents:
            all_skills[intent] = wrapper
            params_extractors[intent] = params_regex

        return wrapper

    return inner


def EntitiesToDict(e):
    result = {}
    for ent in e:
        result[ent['entity']] = ent['value']

    return result



async def TryRunCommand(phrase):
    try:
        parsed = await GetNluData(phrase)
        
        if len(parsed['error']) == 0:
            parsed = parsed['data']
        else:
            print(parsed['error'])
            return

        if parsed['intent']['confidence'] >= 0.89 and parsed['intent']['name'] in all_skills.keys():
            sk = all_skills[parsed['intent']['name']]
            reg = params_extractors[parsed['intent']['name']]
            match = re.match(reg,phrase,re.IGNORECASE)
            print(match,reg)
            if match:
                await all_skills[parsed['intent']['name']](phrase, match.groups())
                return

        TextToSpeech("I cannot answer that yet.")
    except Exception as e:
        print(e)
        print(traceback.format_exc())
    return

