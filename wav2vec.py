from os import path, listdir, getcwd
from transformers import Wav2Vec2ForCTC, Wav2Vec2Tokenizer, Wav2Vec2Processor
from core.threads.voice import StartVoice
import torch
import numpy as np
import sounddevice as sd
from threading import Thread
import time
import webrtcvad
from queue import Queue
vad = webrtcvad.Vad()

output_dir = path.join(getcwd(), 'wav2vec', 'train_output')


def load_model():
    # tokenizer = Wav2Vec2Processor.from_pretrained(
    #     'facebook/wav2vec2-large-960h-lv60')
    # model = Wav2Vec2ForCTC.from_pretrained(
    #     'facebook/wav2vec2-large-960h-lv60')

    tokenizer = Wav2Vec2Processor.from_pretrained(
        output_dir)
    model = Wav2Vec2ForCTC.from_pretrained(
        output_dir)

    return tokenizer, model.float()


TOKENIZER, MODEL = load_model()


def do_inference(audio):
    print("PERFORMING INFERENCE")
    input_vals = TOKENIZER(audio, sampling_rate=16000,
                           return_tensors="pt").input_values.float()

    logits = MODEL(input_vals).logits

    predicted_ids = torch.argmax(logits, dim=-1)

    transcription: str = TOKENIZER.decode(predicted_ids[0])

    capitalized = False

    new_transcription = ""
    for word in transcription.split(" "):
        if not capitalized:
            new_transcription += word.lower().capitalize() + " "
            capitalized = True
        else:
            new_transcription += word.lower() + " "

        if "." in word or "?" in word or "!" in word:
            capitalized = False

    print("RESULT", new_transcription)
    return new_transcription.strip()


model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                              model='silero_vad',
                              force_reload=True,
                              onnx=False, trust_repo=True)

(get_speech_timestamps,
 save_audio,
 read_audio,
 VADIterator,
 collect_chunks) = utils

vad_buff = Queue()
inference_buff = Queue()

FRAME_WINDOW = 5
MAX_WINDOW_TRIES = 6


def vad_thread():
    global vad_buff
    global inference_buff
    current_speech = b''
    frame_window = [b'' for i in range(FRAME_WINDOW)]
    window_tries = 0
    contains_speech = False
    while True:
        chunk = vad_buff.get()
        if chunk is not None:

            frame_window.append(chunk)
            frame_window.pop(0)

            is_speech = len(get_speech_timestamps(np.frombuffer(
                b''.join(frame_window), dtype='int16').copy(), model, sampling_rate=16000)) > 0
            if is_speech:
                contains_speech = True
                current_speech += chunk
                window_tries = 0
                #print("Detected audio, reseting counter", window_tries)
            elif window_tries < len(frame_window):
                current_speech += chunk
                window_tries += 1
                #print("No Audio Trying again", window_tries)
                continue
            else:
                window_tries = 0
                frame_window = [b'' for i in range(FRAME_WINDOW)]
                if contains_speech:
                    inference_buff.put(current_speech)
                    contains_speech = False

                current_speech = b''


def inference_thread():
    global inference_buff
    while True:
        chunk = inference_buff.get()
        if chunk is not None:
            sd.play(np.frombuffer(chunk, dtype='int16'),
                    samplerate=16000)
            transcription = do_inference(
                np.frombuffer(chunk, dtype='int16'))
            if len(transcription) > 0:
                print(transcription)


def OnAudio(chunk):
    global vad_buff
    vad_buff.put(chunk)


Thread(target=vad_thread, daemon=True, group=None).start()
Thread(target=inference_thread, daemon=True, group=None).start()
StartVoice(OnAudio, samplerate=16000, device=None, chunk=5000)
# print(sd.query_devices())
while True:
    time.sleep(100)

# def input_handler():
#     global collect_audio
#     global current_chunk
#     while True:
#         task = input('What do you want to do')
#         if task == '1':
#             collect_audio = not collect_audio
#             print(
#                 "collecting audio data" if collect_audio else "stopped collecting audio data")
#             if collect_audio:
#                 print('reset bytes')
#                 current_chunk = b''
#         elif task == '2':
#             print(do_inference(np.frombuffer(current_chunk, dtype='int16')))
#             # sd.play(, 16000)


# Thread(target=input_handler, daemon=True, group=None).start()
