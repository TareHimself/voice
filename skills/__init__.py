from os.path import dirname, basename, isfile, join
import glob
import re

# import all skills
modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]

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
    for key in all_skills:
        match = re.findall(key, phrase, re.IGNORECASE)
        if len(match) > 0:
            all_skills[key](phrase, match)
            return True

    return False
