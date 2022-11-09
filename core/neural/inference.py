import torch
from core.neural.model import IntentsNeuralNet
from core.neural.utils import tokenize, bag_of_words


class IntentInference:
    def __init__(self, model_path):
        self.data = torch.load(model_path)
        self.model = IntentsNeuralNet(
            self.data['input'], self.data['hidden'], self.data['output'])
        self.model.load_state_dict(self.data['state'])
        self.model.eval()

    def GetIntent(self, msg: str):
        sentence = tokenize(msg)
        x = bag_of_words(sentence, self.data['words'])
        x = torch.from_numpy(x.reshape(1, x.shape[0])).float()
        output = self.model(x)
        _, predicated = torch.max(output, dim=1)

        probs = torch.softmax(output, dim=1)
        prob = probs[0][predicated.item()]

        return prob.item(), self.data['tags'][predicated.item()]
