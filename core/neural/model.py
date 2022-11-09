import torch

from torch import nn, mm, Tensor
import torch.nn.functional as F


class IntentsNeuralNet(nn.Module):
    def __init__(self, bag_size, hidden_size, num_classes):
        super().__init__()
        # Rasa's embedding layer is actually a "dense embedding layer" which is just a Keras dense layer
        # equivalent to a PyTorch Linear layer.
        self.fc = nn.Sequential(nn.Linear(bag_size, hidden_size), nn.ReLU(), nn.Linear(
            hidden_size, hidden_size), nn.ReLU(), nn.Linear(hidden_size, num_classes))

    def forward(self, features: Tensor):
        return self.fc(features)
