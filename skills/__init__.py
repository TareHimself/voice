import re

all_skills = {}


def Skill(regex):
    def inner(func):
        def wrapper(*args,**kwargs):
            try:
                func(*args,**kwargs)
            except Exception as e:
                print(e)

        all_skills[regex] = wrapper
        return wrapper

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
