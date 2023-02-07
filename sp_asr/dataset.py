import torch
import torchaudio
from torch.utils.data import Dataset
from os import path, getcwd, listdir
from torchaudio.functional import resample


def map_data(data: tuple[str, str]):
    file, full_path = data
    data_waveform, rate_of_sample = torchaudio.load(full_path)
    return (resample(data_waveform, rate_of_sample, 16000), "", file.split('.')[0].upper().replace(',', ''), "", "", "")


class CustomAsrDataset(Dataset):

    def __init__(self) -> None:
        super().__init__()
        DATA_PATH = path.join(getcwd(), "audio")
        mapped = list(map(map_data, map(lambda a: (
            a, path.join(DATA_PATH, a)), listdir(DATA_PATH))))
        self.data = mapped + mapped + mapped

    def __getitem__(self, index):
        return self.data[index]

    def __len__(self) -> int:
        return len(self.data)


# print(len(CustomAsrDataset()))
