import json
import numpy as np
import torch
import torch.nn as nn
from nltk_utils import tokenize, stem, bag_of_words
from model import NeuralNet
from torch.utils.data import Dataset, DataLoader
from core.logger import log


class IntentsDataset(Dataset):
    def __init__(self, d: json):
        xy = []
        self.tags = []
        all_x = []
        for intent_obj in d['intents']:
            tag = intent_obj['intent']
            self.tags.append(tag)
            for example in intent_obj['examples']:
                e = tokenize(example)
                all_x.extend(e)
                xy.append((e, tag))

        ignore_words = ['?', '!', '.', ',']
        all_x = sorted(set([stem(w) for w in all_x if w not in ignore_words]))
        self.tags = sorted(set(self.tags))

        self.x_train = []
        self.y_train = []

        for (tokenized, tag) in xy:
            bag = bag_of_words(tokenized, all_x)
            self.x_train.append(bag)

            label = self.tags.index(tag)
            self.y_train.append(label)

    def __len__(self):
        return len(self.x_train)

    def __getitem__(self, idx):
        return self.x_train[idx], self.y_train[idx]


def train(intents: json, batch_size=4, hidden_size=8, learning_rate=0.001, epochs=1000):

    dataset = IntentsDataset(intents)

    train_loader = DataLoader(
        dataset=dataset, batch_size=batch_size, num_workers=0, shuffle=True)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = NeuralNet(len(dataset.x_train[0]), hidden_size, len(
        dataset.tags)).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    for epoch in range(epochs):
        for idx, data in enumerate(train_loader):
            words, labels = data
            words = words.to(device)
            labels = labels.to(device)

            outputs = model(words)

            loss = criterion(outputs, labels)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        if (epoch + 1) % int(0.1 * epochs) == 0:
            log(f'epoch {epoch + 1}/{epochs}, loss={loss.item():.4f}')

    log(f'final loss, loss={loss.item():.4f}')
