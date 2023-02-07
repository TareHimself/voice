from core.numwrd import wrd2num, allDigitsToText, allTextToDigits, num2wrd
from core.strtime import string_to_time
# print(string_to_time("Remind me to sleep in one hundred days"))
# allTextToDigits("What is seventeen point five eight seven nine times ninety")


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
            print(test_buff)
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

            print(result)

        if len(test_buff) > 0:
            result += f"{wrd2num(''.join(test_buff))}"
            test_buff = []

        return result
    except ValueError as e:
        return ''


print(parse_string_to_math("What is ten times fifteen"))
