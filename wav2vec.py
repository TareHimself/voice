from transformers import Wav2Vec2ForCTC, Wav2Vec2Tokenizer, Wav2Vec2Processor
from core.threads.voice import StartVoice
import torch
import numpy as np
import sounddevice as sd
from threading import Thread
import time


def load_model():
    tokenizer = Wav2Vec2Processor.from_pretrained(
        'facebook/wav2vec2-large-960h-lv60')
    model = Wav2Vec2ForCTC.from_pretrained(
        'facebook/wav2vec2-large-960h-lv60')

    return tokenizer, model.float()


TOKENIZER, MODEL = load_model()


def do_inference(audio):
    input_vals = TOKENIZER(audio, sampling_rate=16000,
                           return_tensors="pt").input_values.float()

    logits = MODEL(input_vals).logits

    predicted_ids = torch.argmax(logits, dim=-1)

    transcription = TOKENIZER.decode(predicted_ids[0])

    return transcription


collect_audio = False

current_chunk = b''


def OnAudio(chunk):
    global collect_audio
    global current_chunk
    if collect_audio:
        current_chunk += chunk


def input_handler():
    global collect_audio
    global current_chunk
    while True:
        task = input('What do you want to do')
        if task == '1':
            collect_audio = not collect_audio
            print(
                "collecting audio data" if collect_audio else "stopped collecting audio data")
            if collect_audio:
                print('reset bytes')
                current_chunk = b''
        elif task == '2':
            print(do_inference(np.frombuffer(current_chunk, dtype='int16')))
            # sd.play(, 16000)


Thread(target=input_handler, daemon=True, group=None).start()
StartVoice(OnAudio, device=4)
while True:
    time.sleep(100)
