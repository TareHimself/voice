import asyncio
from io import BytesIO

import requests
from typing import Callable

from events import global_emitter
import threading
from time import sleep


def TextToSpeech(msg):
    global_emitter.emit('send_speech_voice', msg)


def DisplayUiMessage(msg):
    global_emitter.emit('send_speech_text', msg, True)


def EndCommand():
    global_emitter.emit('send_command_end')


def GetFollowUp(callback, args=[], kwargs={}):
    global_emitter.emit('start_wait_followup')

    def OnResultReceived(msg):
        global_emitter.emit('stop_wait_followup')
        args.append(msg)
        global_emitter.off('send_followup_text', OnResultReceived)
        callback(*args, **kwargs)

    global_emitter.on('send_followup_text', OnResultReceived)

def DownloadFile(url: str, OnProgress: Callable[[int, int], None] = lambda t, p: None):
    f = BytesIO()
    r = requests.get(url, stream=True)
    total = r.headers["Content-Length"]

    for chunk in r.iter_content(1024):
        f.write(chunk)
        OnProgress(total, f.getbuffer().nbytes)

    return f