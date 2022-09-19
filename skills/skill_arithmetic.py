from datetime import datetime, timezone
from events import global_emitter
from skills import RegisterSkill
from word2number import w2n

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


def DoMath(phrase, match):
    result = ParseStringToMath(match[0][1])
    if len(result):
        global_emitter.emit('say', "The answer is {}".format(str(eval(result))), True)
    else:
        global_emitter.emit('say', 'Failed To Parse Mathematical Expression', True)


def RestoreWindow(phrase, match):
    global_emitter.emit('window_action', "restore")


RegisterSkill(DoMath, r"^(math|calculate|arithmetic)[\s]+(.+)")
