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


def parse_string_to_math(expr):
    latest_unconverted = ""
    result = ""
    try:
        for word in expr.split():

            if word.lower() in token_keys:

                if len(latest_unconverted.strip()) > 0:
                    result += str(wrd2num(latest_unconverted))
                    latest_unconverted = ""
                result += tokens[word]
            else:
                latest_unconverted += word.strip() + " "

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
