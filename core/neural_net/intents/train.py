import json
from os import path, getcwd
from torchtext.data.utils import get_tokenizer
from torchtext.vocab import build_vocab_from_iterator
import numpy as np
import torch
import torch.nn as nn
from nltk_utils import tokenize, stem, bag_of_words
from model import IntentsNeuralNet
from torch.utils.data import Dataset, DataLoader
from core.logger import log


class IntentsDataset(Dataset):
    def __init__(self, d: dict):
        xy = []
        self.train_y = []
        self.train_x = []
        self.all_x = []


        tokenizer = get_tokenizer('basic_english')
        tokens = []

        for intent_obj in d['intents']:
            tag = intent_obj['intent']
            self.train_y.append(tag)
            self.train_x = intent_obj['examples']
            for example in intent_obj['examples']:
                e = tokenizer(example)
                self.all_x.extend(e)
                xy.append((e, tag))

        vocab_x = build_vocab_from_iterator([set(self.all_x)], specials=["<unk>"])
        vocab_x.set_default_index(vocab_x["<unk>"])

        vocab_y = build_vocab_from_iterator([set(self.train_y)], specials=["<unk>"])
        vocab_y.set_default_index(vocab_y["<unk>"])

        self.text_pipeline = lambda x: vocab_x(tokenizer(x))
        self.label_pipeline = lambda x: vocab_y([x])[0]
        print(list(map(self.text_pipeline,self.train_x[0])),self.train_x)
        #print(text_pipeline("Play in the name of love"), label_pipeline('skill_time'))

        # for intent_obj in d['intents']:
        #     tag = intent_obj['intent']
        #     self.tags.append(tag)
        #     for example in intent_obj['examples']:
        #         e = tokenize(example)
        #         self.all_x.extend(e)
        #         xy.append((e, tag))

    #     ignore_words = ['?', '!', '.', ',']
    #     self.all_x = sorted(set([stem(w) for w in self.all_x if w not in ignore_words]))
    #     self.tags = sorted(set(self.tags))
    #
    #     self.x_train = []
    #     self.y_train = []
    #
    #     for (tokenized, tag) in xy:
    #         bag = bag_of_words(tokenized, self.all_x)
    #         self.x_train.append(bag)
    #
    #         label = self.tags.index(tag)
    #         self.y_train.append(label)
    #
    # def __len__(self):
    #     return len(self.x_train)
    #
    # def __getitem__(self, idx):
    #
    #     return torch.tensor(self.x_train[idx]).float(), torch.tensor(self.y_train[idx]).float()


def train(intents: dict, save_path, batch_size=4, hidden_size=8, learning_rate=0.001, epochs=1000):
    dataset = IntentsDataset(intents)

    return
    train_loader = DataLoader(
        dataset=dataset, batch_size=batch_size, num_workers=0, shuffle=True)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    input_size = len(dataset.x_train[0])
    output_size = len(dataset.train_y)
    model = IntentsNeuralNet(input_size, hidden_size, output_size).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    for epoch in range(epochs):
        for idx, label_word in enumerate(train_loader):
            words, labels = label_word
            words = words.to(device)
            labels = labels.to(device)
            outputs = model(words)

            loss = criterion(outputs, labels.long())

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        if (epoch + 1) % int(0.1 * epochs) == 0:
            log(f'epoch {epoch + 1}/{epochs}, loss={loss.item():.4f}')

    log(f'final loss, loss={loss.item():.4f}')

    data_to_save = {
        "state": model.state_dict(),
        "input": input_size,
        "output": output_size,
        "hidden": hidden_size,
        "words": dataset.all_x,
        "tags": dataset.train_y
    }

    torch.save(data_to_save, save_path)


with open(path.join(getcwd(), '../../../skills', 'default', 'intents.json'), 'r') as f:
    data = json.load(f)

    train(data, save_path='test_model.ptf')

# from inference import IntentInference
#
# m = IntentInference(path.join(getcwd(),'test_model.ptf'))
#
# while True:
#     msg = input('Ask Me Anything?')
#     print(m.GetIntent(msg))
