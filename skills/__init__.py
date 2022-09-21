import inspect
import re

all_skills = {}


def skill(regex):
    def inner(func):
        all_skills[regex] = func
        return func

    return inner


def RegisterSkill(s, regex):
    setattr(s, 'reg', regex)
    return


def TryRunCommand(phrase):
    print(phrase)
    for key in all_skills:
        match = re.findall(key, phrase, re.IGNORECASE)
        if len(match) > 0:
            all_skills[key](phrase, match)
            return True

    return False
