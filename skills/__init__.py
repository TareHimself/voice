import re

all_skills = {}


def Skill(regex):
    def inner(func):
        all_skills[regex] = func
        return func

    return inner


def RegisterSkill(s, regex):
    setattr(s, 'reg', regex)
    return


def GetCommand(phrase):
    for key in all_skills:
        if re.match(key, phrase, re.IGNORECASE):
            groups = list(re.search(key, phrase, re.IGNORECASE).groups())
            return [all_skills[key], phrase, [x for x in groups if x is not None]]

    return None
