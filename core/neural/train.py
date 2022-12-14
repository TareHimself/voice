import numpy as np
import torch
import torch.nn as nn
from core.neural.datasets import IntentsDataset
from core.neural.model import IntentsNeuralNet
from torch.utils.data import DataLoader
from core.logger import log
from os import path
from core.neural.utils import hash_intents, expand_all_examples
from tqdm import tqdm

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def train_intents(intents: list, save_path: str, batch_size=8, learning_rate=0.001, epochs=200):
    expand_all_examples(intents)
    intents_hash = hash_intents(intents)
    if path.exists(save_path):
        old_data: dict = torch.load(save_path)
        if old_data.get('hash', "") == intents_hash:
            log("No need to train new model, loading existing")
            return

    log("Training new model")
    dataset = IntentsDataset(intents)

    def collate_data(batch):
        nonlocal dataset
        # rearrange a batch and compute offsets too
        # needs a global vocab and tokenizer
        label_lst, review_lst, offset_lst = [], [], [0]
        for (_lbl, _rvw) in batch:
            label_lst.append(int(_lbl))  # string to int
            idxs = []
            for tok in _rvw:
                idxs.append(dataset.vocab[tok])

            idxs = torch.tensor(idxs, dtype=torch.int64)  # to tensor
            review_lst.append(idxs)
            offset_lst.append(len(idxs))

        label_lst = torch.tensor(label_lst, dtype=torch.int64).to(device)
        offset_lst = torch.tensor(offset_lst[:-1]).cumsum(dim=0).to(device)
        review_lst = torch.cat(review_lst).to(device)  # 2 tensors to 1

        return label_lst, review_lst, offset_lst

    train_loader = DataLoader(
        dataset=dataset, batch_size=batch_size, num_workers=0, shuffle=True, collate_fn=collate_data)

    input_size = len(dataset.vocab)
    embed_dim = 300
    hidden_size = 128
    output_size = len(dataset.tags)

    model = IntentsNeuralNet(input_size, embed_dim,
                             hidden_size, output_size).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    loading_bar = tqdm(
        total=epochs, desc=f'epoch {0}/{epochs} ::  Accuracy unknown :: loss unknown')

    for epoch in range(epochs):
        total_accu, total_count = 0, 0
        for idx, data in enumerate(train_loader):
            label, text, offsets = data

            # print(label, text)

            outputs = model(text, offsets)
            loss = criterion(outputs, label)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_accu += (outputs.argmax(1) == label).sum().item()
            total_count += label.size(0)

        accu_val = total_accu / total_count
        loading_bar.update()
        loading_bar.set_description_str(
            f'epoch {epoch + 1}/{epochs} ::  Accuracy {(accu_val * 100):.4f} :: loss {loss.item():.4f}')

    data_to_save = {
        "state": model.state_dict(),
        "input": input_size,
        "e_dim": embed_dim,
        "hidden": hidden_size,
        "output": len(dataset.tags),
        "words": dataset.words,
        "tags": dataset.tags,
        "hash": intents_hash
    }

    torch.save(data_to_save, save_path)
