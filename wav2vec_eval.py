from huggingsound import TrainingArguments, ModelArguments, SpeechRecognitionModel, TokenSet
from os import path, listdir, getcwd
output_dir = path.join(getcwd(), 'wav2vec', 'train_output')
model = SpeechRecognitionModel(output_dir)


# first of all, you need to define your model's token set
# however, the token set is only needed for non-finetuned models
# if you pass a new token set for an already finetuned model, it'll be ignored during training
tokens = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
          "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "'", ","]
token_set = TokenSet(tokens)

test_data = []
for file in listdir(path.join(getcwd(), 'wav2vec', 'audio')):
    test_data.append(path.join(getcwd(), 'wav2vec', 'audio', file))

transcriptions = model.transcribe(test_data)

print(transcriptions)
