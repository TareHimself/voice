import torch
import torchtext as tt
from tqdm import tqdm
from torch.utils.data import Dataset
from core.neural.utils import tokenize, build_vocab


class IntentsDataset(Dataset):
    def __init__(self, d: list, tokenizer=tokenize):
        self.tags = []
        self.train_x = []
        self.train_y = []
        self.tokenizer = tokenizer

        for idx in range(len(d)):
            tag = d[idx]['tag']
            self.tags.append(tag)
            for example in d[idx]['examples']:
                self.train_y.append(idx)
                self.train_x.append(self.tokenizer(example))

        self.words = list(set(self.train_x))

        self.vocab = build_vocab(self.words)

    def __len__(self):
        return len(self.train_x)

    def __getitem__(self, idx):
        return self.train_y[idx], self.train_x[idx]
