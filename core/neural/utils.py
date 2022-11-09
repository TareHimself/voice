from core.constants import DIRECTORY_DATA_CORE
from nltk.stem.porter import PorterStemmer
import numpy as np
from nltk import word_tokenize
import nltk
from os import path

stemmer = PorterStemmer()


def tokenize(sentence):
    return word_tokenize(sentence)


def stem(word):
    return stemmer.stem(word.lower())


def bag_of_words(tokenized, words):
    tokenized = [stem(w) for w in tokenized]

    bag = np.zeros(len(words), dtype=np.float)

    for idx, wrd in enumerate(words):
        if wrd in tokenized:
            bag[idx] = float(1.0)

    return bag
