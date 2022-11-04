import json
from os import path, getcwd
from torchtext.data.utils import get_tokenizer
from torchtext.vocab import build_vocab_from_iterator
import numpy as np
from tqdm import tqdm
import torch
import torch.nn as nn
from nltk_utils import tokenize, stem, bag_of_words
from model import IntentsNeuralNet
from torch.utils.data import Dataset, DataLoader
from core.logger import log
from transformers import BertTokenizer


class IntentsDataset(Dataset):
    def __init__(self, d: dict):
        self.labels = []
        self.train_x = []
        self.train_y = []

        tokenizer = BertTokenizer.from_pretrained('bert-base-cased')
        tokens = []

        for intent_obj in d['intents']:
            tag = intent_obj['intent']
            self.labels.append(tag)
            self.train_x = intent_obj['examples']
            for example in intent_obj['examples']:
                self.train_x.append(tokenizer(example, padding='max_length', max_length=512, truncation=True,
                                                return_tensors="pt"))
                self.train_y.append(tag)

    def __len__(self):
        return len(self.train_xy)

    def __getitem__(self, idx):
        return self.train_xy[idx]


def train(intents: dict, save_path, batch_size=4, hidden_size=8, learning_rate=0.001, epochs=1000):
    dataset = IntentsDataset(intents)

    train_loader = DataLoader(
        dataset=dataset, batch_size=batch_size, num_workers=0, shuffle=True)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    output_size = len(dataset.labels)
    model = IntentsNeuralNet( output_size).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    for epoch in range(epochs):
        for idx , (train_input, train_label) in tqdm(train_loader):
            train_label = train_label.to(device)
            mask = train_input['attention_mask'].to(device)
            input_id = train_input['input_ids'].squeeze(1).to(device)

            output = model(input_id, mask)

            batch_loss = criterion(output, train_label.long())

            acc = (output.argmax(dim=1) == train_label).sum().item()

            model.zero_grad()
            batch_loss.backward()
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
