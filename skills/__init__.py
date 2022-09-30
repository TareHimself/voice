import re
from os import path, getcwd

from rasa.core.agent import Agent
import asyncio

agent = Agent.load(model_path=path.join(getcwd(), 'nlu.tar.gz'))
all_skills = {}
def Skill(*intents):
    def inner(func):
        def wrapper(*args,**kwargs):
            try:
                func(*args,**kwargs)
            except Exception as e:
                print(e)

        for intent in intents:
            all_skills[intent] = wrapper

        return wrapper

    return inner


def RegisterSkill(s, regex):
    setattr(s, 'reg', regex)
    return


def GetCommand(phrase):
    parsed = asyncio.run(agent.parse_message(message_data=phrase))

    print(parsed)


    return None
