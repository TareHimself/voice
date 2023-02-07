from huggingsound import TrainingArguments, ModelArguments, SpeechRecognitionModel, TokenSet
from os import path, listdir, getcwd
model = SpeechRecognitionModel("facebook/wav2vec2-base")
output_dir = path.join(getcwd(), 'wav2vec', 'train_output')

# first of all, you need to define your model's token set
# however, the token set is only needed for non-finetuned models
# if you pass a new token set for an already finetuned model, it'll be ignored during training
tokens = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
          "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "'"]
token_set = TokenSet(tokens)

train_data = []
for file in listdir(path.join(getcwd(), 'wav2vec', 'audio')):
    train_data.append({
        "path": path.join(getcwd(), 'wav2vec', 'audio', file),
        "transcription": f"{file[:-4].upper()}</s>"
    })
    train_data.append({
        "path": path.join(getcwd(), 'wav2vec', 'audio', file),
        "transcription": f"{file[:-4].upper()}</s>"
    })
targs = TrainingArguments()

targs.max_steps = 2000
targs.per_device_train_batch_size = 2
targs.overwrite_output_dir = True
targs.logging_steps = 1

eval_data = train_data
# and finally, fine-tune your model
model.finetune(
    output_dir,
    train_data=train_data,
    token_set=token_set,
    training_args=targs
)
