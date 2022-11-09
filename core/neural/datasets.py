import torch
from tqdm import tqdm
from torch.utils.data import Dataset
from core.neural.utils import tokenize, bag_of_words


class IntentsDataset(Dataset):
    def __init__(self, d: list, tokenizer=tokenize, get_bag=bag_of_words):
        self.tags = []
        self.train_x = []
        self.train_y = []
        self.words = []
        self.tokenizer = tokenizer
        self.get_bag = get_bag
        temp = []
        for idx in range(len(d)):
            tag = d[idx]['tag']
            self.tags.append(tag)
            for example in d[idx]['examples']:
                self.words.extend(self.tokenizer(example))
                temp.append((idx, example))

        self.words = list(set(self.words))

        for tag_idx, example in temp:
            self.train_y.append(tag_idx)
            self.train_x.append(torch.Tensor(get_bag(self.tokenizer(
                example), self.words)).to(dtype=torch.long))

        temp = []

    def __len__(self):
        return len(self.train_x)

    def __getitem__(self, idx):
        return self.train_y[idx], self.train_x[idx]
