from os import path, getcwd, listdir
import traceback
from core.constants import NLU_PATH, DATA_PATH
from core.utils import GetNluData, StartSkill, EndSkill, TextToSpeech

all_skills = {}


def Skill(*intents):
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

        return wrapper

    return inner


def EntitiesToDict(e):
    result = {}
    for ent in e:
        result[ent['entity']] = ent['value']

    return result



async def TryRunCommand(phrase):
    parsed = await GetNluData(phrase)

    if len(parsed['error']) == 0:
        parsed = parsed['data']
    else:
        print(parsed['error'])
        return

    if parsed['intent']['confidence'] >= 0.89 and parsed['intent']['name'] in all_skills.keys():
        await all_skills[parsed['intent']['name']](phrase, EntitiesToDict(parsed['entities']))
    else:
        TextToSpeech("I cannot answer that yet.")

    return

