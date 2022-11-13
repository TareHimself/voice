import torch
from core.neural.model import IntentsNeuralNet
from torchtext.data.utils import get_tokenizer
from torchtext.vocab import build_vocab_from_iterator
tokenizer = get_tokenizer('basic_english')


class IntentInference:
    def __init__(self, model_path):
        self.data = torch.load(model_path)
        self.model = IntentsNeuralNet(
            self.data['input'], self.data['e_dim'], self.data['hidden'], self.data['output'])

        self.vocab = build_vocab_from_iterator([self.data['words']], min_freq=1,
                                               specials=['<unk>'])
        self.vocab.set_default_index(self.vocab["<unk>"])
        self.model.load_state_dict(self.data['state'])
        self.model.eval()

    def get_intent(self, msg: str):
        global tokenizer
        sentence = tokenizer(msg)
        x = self.vocab(sentence)
        print(x)
        x = torch.IntTensor(x)
        output = self.model(x, torch.IntTensor([0]))
        _, predicated = torch.max(output, dim=1)

        probs = torch.softmax(output, dim=1)
        prob = probs[0][predicated.item()]

        return prob.item(), self.data['tags'][predicated.item()]
