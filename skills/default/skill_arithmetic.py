from core.skills import Skill
from word2number import w2n

from core.utils import TextToSpeech

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


def ParseStringToMath(expr):
    latest_unconverted = ""
    result = ""
    try:
        for word in expr.split():

            if word.lower() in token_keys:

                if len(latest_unconverted.strip()) > 0:
                    result += str(w2n.word_to_num(latest_unconverted))
                    latest_unconverted = ""
                result += tokens[word]
            else:
                latest_unconverted += word.strip() + " "

        if len(latest_unconverted.strip()) > 0:
            result += str(w2n.word_to_num(latest_unconverted))

        return result
    except ValueError as e:
        return ''


@Skill(["skill_arithmetic"],r"(?:(?:math|calculate|arithmetic|what is)\s?)?(.*)")
async def DoMath(phrase, args):
    result = ParseStringToMath(args[0])
    if len(result):
        TextToSpeech("The answer is {}".format(str(eval(result))))
    else:
        TextToSpeech('Failed To Parse Mathematical Expression')
