from gc import callbacks
import time
from regex import F
import torch
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import pyaudio
import librosa
import numpy as np

processor = Wav2Vec2Processor.from_pretrained('yongjian/wav2vec2-large-a')
model = Wav2Vec2ForCTC.from_pretrained('yongjian/wav2vec2-large-a')
p = pyaudio.PyAudio()


def asr_transcript(speech):
    """This function generates transcripts for the provided audio input
    """
    # Tokenize
    input_values = processor(speech, return_tensors="pt").input_values
    # Take logits
    logits = model(input_values).logits
    # Take argmax
    predicted_ids = torch.argmax(logits, dim=-1)
    # Get the words from predicted word ids
    transcription = processor.decode(predicted_ids[0])
    # Output is all upper case
    return transcription


def OnVoiceData(audio_chunk, frame_count, time_info, status):
    try:

        float64_buffer = np.frombuffer(audio_chunk, dtype=np.int16) / 32767
        text = asr_transcript(float64_buffer)
        text = text.lower()
        sample_length = len(float64_buffer) / 16000  # length in sec
        if text != "":
            print(text)

    except Exception as e:
        print("ERROR | ", e)


FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
# A frame must be either 10, 20, or 30 ms in duration for webrtcvad
FRAME_DURATION = 30
CHUNK = int(RATE * FRAME_DURATION / 1000)
RECORD_SECONDS = 50

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                stream_callback=OnVoiceData)

stream.start_stream()

while True:
    time.sleep(100000)
