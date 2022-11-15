from core.constants import DIRECTORY_DATA_CORE
from nltk.stem.porter import PorterStemmer
import numpy as np
from nltk import word_tokenize
import nltk
from os import path
from torchtext.data.utils import get_tokenizer
from torchtext.vocab import build_vocab_from_iterator

stemmer = PorterStemmer()
_tokenizer = get_tokenizer('basic_english')

def build_vocab(words: list):
    vocab = build_vocab_from_iterator([words], min_freq=1,
                                      specials=['<unk>'])

    vocab.set_default_index(vocab["<unk>"])

    return vocab

def tokenize(text: str):
    return _tokenizer(text)
