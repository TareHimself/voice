from torchtext.data.utils import get_tokenizer
from torchtext.vocab import build_vocab_from_iterator
import numpy as np
import torch
import torch.nn as nn
from core.neural.datasets import IntentsDataset
from core.neural.model import IntentsNeuralNet
from torch.utils.data import DataLoader
from core.logger import log

# from core.logger import log

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def train_intents(intents: list, save_path, batch_size=8, learning_rate=0.001, epochs=1000):
    dataset = IntentsDataset(intents, tokenizer=get_tokenizer('basic_english'))

    train_loader = DataLoader(
        dataset=dataset, batch_size=batch_size, num_workers=0, shuffle=True)

    input_size = len(dataset.words)
    hidden_size = 256
    output_size = len(dataset.tags)

    model = IntentsNeuralNet(input_size, hidden_size, output_size).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    for epoch in range(epochs):
        total_accu, total_count = 0, 0
        for idx, data in enumerate(train_loader):
            label, text = data
            label = label.to(dtype=torch.long).to(device)
            text = text.float().to(device)

            # print(label, text)

            outputs = model(text)
            loss = criterion(outputs, label)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_accu += (outputs.argmax(1) == label).sum().item()
            total_count += label.size(0)

        accu_val = total_accu / total_count

        if int(0.1 * epochs) == 0 or (epoch + 1) % int(0.1 * epochs) == 0:
            log(f'epoch {epoch + 1}/{epochs} ::  Accuracy {(accu_val * 100):.4f} :: loss={loss.item():.4f}')

    log(f'Final Stats ::  Accuracy {(accu_val * 100):.4f} :: loss={loss.item():.4f}')

    data_to_save = {
        "state": model.state_dict(),
        "input": input_size,
        "output": len(dataset.tags),
        "hidden": hidden_size,
        "words": dataset.words,
        "tags": dataset.tags
    }

    torch.save(data_to_save, save_path)
