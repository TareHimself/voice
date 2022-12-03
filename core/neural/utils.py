import hashlib
import re
from core.constants import DIRECTORY_DATA_CORE
from torchtext.data.utils import get_tokenizer
from torchtext.vocab import build_vocab_from_iterator
from core.numwrd import num2wrd

_tokenizer = get_tokenizer('basic_english')

EXTRACT_VARIATIONS_REGEX = r"\[(.*?)\]"


def build_vocab(words: list):
    vocab = build_vocab_from_iterator([words], min_freq=1,
                                      specials=['<unk>'])

    vocab.set_default_index(vocab["<unk>"])

    return vocab


def tokenize(text: str):
    tokens = []
    split_tok = text.split(" ")

    for tok in split_tok:
        cur = tok.strip().lower()
        if len(cur) <= 0:
            continue

        if cur.isnumeric():
            tokens.append(num2wrd(int(cur)))
        else:
            tokens.append(cur)

    return tokens
    #
    # tokens = _tokenizer(text)
    # return


def replace_at_depth(current_value, cur_depth, variations):
    if cur_depth < len(variations):
        converted = []
        for variation in variations[cur_depth]:
            replaced_current = current_value.replace(
                f"${cur_depth}", variation.strip())
            converted.extend(replace_at_depth(
                replaced_current, cur_depth + 1, variations))
        return converted
    else:
        return [current_value]


def compute_expanded_example(example: str):
    variations = re.findall(EXTRACT_VARIATIONS_REGEX, example, re.DOTALL)
    replace_template = example
    for i in range(len(variations)):
        replace_template = replace_template.replace(
            f"[{variations[i]}]", f"${i}", 1)

    actual_variations = list(map(lambda a: a.split("|"), variations))

    return replace_at_depth(replace_template, 0, actual_variations)


def expand_all_examples(intents: list):
    for intent in intents:
        tag = intent['tag']
        new_examples = []
        for example in intent['examples']:
            new_examples.extend(compute_expanded_example(example))
        intent['examples'] = new_examples
    return intent


def hash_intents(intents: list):
    final_string = ""
    for intent in intents:
        tag = intent['tag']
        for example in intent['examples']:
            final_string += f'{tag.replace(" ", "")}{example.replace(" ", "")}'

    return hashlib.md5(final_string.encode()).hexdigest()


def increase_size(items: list, target: int):
    start_len = len(items)
    for i in range(max(target - start_len, 0)):
        items.append(items[i % start_len])

    return items
