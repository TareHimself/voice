import torch
import torch.nn as nn


class NeuralNet(nn.Module):
    def __init__(self,input_size,hidden_size,num_classes):
        super().__init__()
        self.fr  = nn.Sequential(
            nn.Linear(input_size,hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size,hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size,num_classes)
            )

    def forward(self,x):
        return self.fr(x)