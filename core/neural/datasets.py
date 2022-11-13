import torch
import torchtext as tt
from tqdm import tqdm
from torch.utils.data import Dataset
from core.neural.utils import tokenize, bag_of_words
from torchtext.data.utils import get_tokenizer


class IntentsDataset(Dataset):
    def __init__(self, d: list, tokenizer=get_tokenizer('basic_english')):
        self.tags = []
        self.train_x = []
        self.train_y = []
        self.words = []
        self.tokenizer = tokenizer
        temp = []

        for idx in range(len(d)):
            tag = d[idx]['tag']
            self.tags.append(tag)
            for example in d[idx]['examples']:
                self.words.extend(self.tokenizer(example))
                temp.append((idx, example))
                self.train_y.append(idx)
                self.train_x.append(self.tokenizer(example))

        self.words = list(set(self.words))

        self.vocab = tt.vocab.build_vocab_from_iterator(
            [self.words], specials=["<unk>"])
        self.vocab.set_default_index(self.vocab["<unk>"])

    def __len__(self):
        return len(self.train_x)

    def __getitem__(self, idx):
        return self.train_y[idx], self.train_x[idx]
