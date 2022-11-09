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

for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print(info.get('name'), info.get('maxInputChannels'),
          info.get('maxOutputChannels'), i)


audio_input = p.open(input_device_index=RESPEAKER_INDEX,
                     format=pyaudio.paInt16,
                     channels=RESPEAKER_CHANNELS,
                     rate=RESPEAKER_RATE,
                     input=True,
                     frames_per_buffer=CHUNK)

audio_output = p.open(input_device_index=20,
                      format=pyaudio.paInt16,
                      channels=RESPEAKER_CHANNELS,
                      rate=RESPEAKER_RATE,
                      frames_per_buffer=CHUNK, output=True)

while True:
    audio_chunk = audio_input.read(
        CHUNK, exception_on_overflow=False)
    if audio_chunk:
        audio_output.write(audio_chunk)
