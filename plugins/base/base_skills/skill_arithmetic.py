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
    test_buff = []
    result = ""
    try:
        for word in expr.split():

            word = word.lower().strip()

            test_buff.append(word)
            test = wrd2num("".join(test_buff))

            if test is None:
                test_buff.pop()
                if len(test_buff) > 0:
                    result += f"{wrd2num(''.join(test_buff))}"
                    test_buff = []
            else:
                continue

            if word in token_keys:
                result += tokens[word]
            elif word in token_values:
                result += word

        if len(test_buff) > 0:
            result += f"{wrd2num(''.join(test_buff))}"
            test_buff = []

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
