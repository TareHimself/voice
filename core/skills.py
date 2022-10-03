from os import path, getcwd
from rasa.core.agent import Agent
from rasa.model_training import train_nlu
from core.constants import NLU_PATH, DATA_PATH
from core.utils import StartSkill, EndSkill, TextToSpeech

if not path.exists(NLU_PATH):
    train_nlu(config=path.join(getcwd(), 'rasa', 'config.yml'), nlu_data=path.join(getcwd(), 'rasa', 'nlu.yml'),
              output=DATA_PATH, fixed_model_name='nlu')

agent = Agent.load(model_path=NLU_PATH)
all_skills = {}


def Skill(*intents):
    def inner(func):
        async def wrapper(*args, **kwargs):
            try:
                StartSkill()
                await func(*args, **kwargs)
                EndSkill()
            except Exception as e:
                print(e)

        for intent in intents:
            all_skills[intent] = wrapper

        return wrapper

    return inner


def EntitiesToDict(e):
    result = {}
    for ent in e:
        result[ent['entity']] = ent['value']

    return result


async def ParsePhrase(phrase):
    return await agent.parse_message(message_data=phrase)


async def TryRunCommand(phrase):
    parsed = await ParsePhrase(phrase)

    if parsed['intent']['confidence'] >= 0.89 and parsed['intent']['name'] in all_skills.keys():
        await all_skills[parsed['intent']['name']](phrase, EntitiesToDict(parsed['entities']))
    else:
        TextToSpeech("I cannot answer that yet.")

    return
