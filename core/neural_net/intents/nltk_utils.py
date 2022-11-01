import nltk
import numpy as np
from nltk.stem.porter import PorterStemmer

# nltk.download('punkt')

stemmer = PorterStemmer()


def tokenize(sentence):
    nltk.word_tokenize(sentence)


def stem(word):
    stemmer.stem(word.lower())


def bag_of_words(tokenized, words):
    tokenized = [stem(w) for w in tokenized]

    bag = np.zeros(len(words), dtype=np.float)

    for idx, wrd in enumerate(words):
        if wrd in tokenized:
            bag[idx] = 1.0

    return bag
