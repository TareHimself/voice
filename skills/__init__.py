import re

all_skills = {}


def skill(s):
    func = s()

    def inner(*args, **kwargs):
        return func(*args, **kwargs)

    all_skills[getattr(func, 'reg')] = inner
    return inner


def RegisterSkill(s, regex):
    setattr(s, 'reg', regex)

    @skill
    def x(*args, **kwargs):
        return s

    return x


def TryRunCommand(phrase):
    print(phrase)
    for key in all_skills:
        match = re.findall(key, phrase, re.IGNORECASE)
        if len(match) > 0:
            all_skills[key](phrase, match)
            return True

    return False
