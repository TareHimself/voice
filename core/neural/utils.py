import hashlib

from core.constants import DIRECTORY_DATA_CORE
from nltk.stem.porter import PorterStemmer
from torchtext.data.utils import get_tokenizer
from torchtext.vocab import build_vocab_from_iterator
from core.numwrd import num2wrd

stemmer = PorterStemmer()
_tokenizer = get_tokenizer('basic_english')


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


def hash_intents(intents: list):
    final_string = ""
    for intent in intents:
        tag = intent['tag']
        for example in intent['examples']:
            final_string += f'{tag.replace(" ", "")}{example.replace(" ", "")}'
    print(final_string)
    return hashlib.md5(final_string.encode()).hexdigest()


def increase_size(items: list, target: int):
    start_len = len(items)
    for i in range(max(target - start_len, 0)):
        items.append(items[i % start_len])

    return items
