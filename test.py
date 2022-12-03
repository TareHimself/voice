import torch

a = torch.tensor([[1,2], [2,5]])

b = torch.tensor([[0.5,2],[2.9,7]])

print(torch.pairwise_distance(a,b))