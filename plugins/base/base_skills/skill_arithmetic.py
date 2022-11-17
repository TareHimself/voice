from core.decorators import Skill
from core.numwrd import wrd2num
from core.assistant import SkillEvent
from plugins.base.text_to_speech import text_to_speech

tokens = {
    "plus": "+",
    "add": '+',
    "divided": '/',
    "by": '',
    "minus": '-',
    "times": '*',
    "multiplied": '*',
}

token_keys = tokens.keys()
token_values = tokens.values()


def parse_string_to_math(expr):
    latest_unconverted = ""
    result = ""
    try:
        for word in expr.split():

            word = word.lower().strip()

            if word.isnumeric():
                result += word + " "
                continue

            if word in token_keys or word in token_values:

                if len(latest_unconverted.strip()) > 0:
                    result += str(wrd2num(latest_unconverted))
                    latest_unconverted = ""
                result += tokens[word] if word in token_keys else word
            else:
                latest_unconverted += word + " "

        if len(latest_unconverted.strip()) > 0:
            result += str(wrd2num(latest_unconverted))

        return result
    except ValueError as e:
        return ''


@Skill(["skill_arithmetic"], r"(?:(?:math|calculate|arithmetic|what is)\s?)?(.*)")
async def do_math(e: SkillEvent, args: list):
    result = parse_string_to_math(args[0])
    if len(result):
        await e.context.handle_response("The answer is {}".format(str(eval(result))))
    else:
        await e.context.handle_response('Failed To Parse Mathematical Expression')
