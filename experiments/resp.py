import pyaudio
import wave

RESPEAKER_RATE = 16000
# change base on firmwares, 1_channel_firmware.bin as 1 or 6_channels_firmware.bin as 6
RESPEAKER_CHANNELS = 1
RESPEAKER_WIDTH = 2
# run getDeviceInfo.py to get index
RESPEAKER_INDEX = 1  # refer to input device id
CHUNK = 1024
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

p = pyaudio.PyAudio()

stream = p.open(
    rate=RESPEAKER_RATE,
    format=p.get_format_from_width(RESPEAKER_WIDTH),
    channels=RESPEAKER_CHANNELS,
    input=True,
    input_device_index=RESPEAKER_INDEX,)

print("* recording")

frames = []

stream = p.open(input_device_index=RESPEAKER_INDEX,
                                format=pyaudio.paInt16,
                                channels=RESPEAKER_CHANNELS,
                                rate=RESPEAKER_RATE,
                                input=True,
                                frames_per_buffer=CHUNK,output=True)

while True:
        audio_chunk = stream.read(
            CHUNK, exception_on_overflow=False)
        if audio_chunk:
            stream.write(audio_chunk)
for i in range(0, int(RESPEAKER_RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()

wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(RESPEAKER_CHANNELS)
wf.setsampwidth(p.get_sample_size(p.get_format_from_width(RESPEAKER_WIDTH)))
wf.setframerate(RESPEAKER_RATE)
wf.writeframes(b''.join(frames))
wf.close()
