from core.numwrd import wrd2num


def convertNumbers(expr: str):
    all_tok = expr.split()
    word_buff = []
    result = ""

    for tok in all_tok:
        possible_num = wrd2num("".join(word_buff) + tok)
        if possible_num is not None:
            word_buff.append(f"{tok} ")
        else:
            if len(word_buff) > 0:
                result += f"{wrd2num(''.join(word_buff))} "
                word_buff = []
            result += tok + " "

    return result


print(convertNumbers("Remind me to sleep at ten twenty five am tomorrow"))