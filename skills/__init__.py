import re
from rasa.cli.utils import get_validated_path
from rasa.model import get_model, get_model_subdirectories
from rasa.core.interpreter import RasaNLUInterpreter
from rasa.shared.nlu.training_data.message import Message

def load_interpreter(model_dir, model):
    path_str = str(pathlib.Path(model_dir) / model)
    model = get_validated_path(path_str, "model")
    model_path = get_model(model)
    _, nlu_model = get_model_subdirectories(model_path)
    return RasaNLUInterpreter(nlu_model)

# Loads the model
mod = load_interpreter(model_dir, model)
# Parses new text
msg = Message({TEXT: text})
for p in interpreter.interpreter.pipeline:
    p.process(msg)
    print(msg.as_dict())

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
    interpreter.parse(phrase)
    for key in all_skills:
        if re.match(key, phrase, re.IGNORECASE):
            groups = list(re.search(key, phrase, re.IGNORECASE).groups())
            return [all_skills[key], phrase, [x for x in groups if x is not None]]

    return None
