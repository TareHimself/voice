import asyncio
import hashlib
import uuid
from io import BytesIO
import aiohttp
import requests
from threading import Thread
from typing import Callable, Union
from core.events import global_emitter
from core.threads import StartTimer, StopTimer


async def GetNluData(phrase):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://proxy.oyintare.dev/nlu/parse?q={}".format(phrase)) as resp:
                nlu_response = await resp.json()
                print(nlu_response)
                if len(nlu_response['error']):
                    return None

                return [nlu_response['data']['intent']['name'], nlu_response['data']['intent']['confidence']]
    except aiohttp.ClientConnectorError as e:
        print(e)
        return None


def TextToSpeech(msg, waitForFinish=False) -> Union[None, asyncio.Future]:
    if not waitForFinish:
        global_emitter.emit('send_speech_voice', msg, None)
        return

    loop = asyncio.get_event_loop()
    task_return = asyncio.Future()

    def OnFinish():
        nonlocal task_return
        loop.call_soon_threadsafe(task_return.set_result, None)

    global_emitter.emit('send_speech_voice', msg, OnFinish)

    return task_return


def DisplayUiMessage(msg):
    print(msg, end='\r')
    global_emitter.emit('send_speech_text', msg, True)


def EndSkill():
    global_emitter.emit('send_skill_end')


def StartSkill():
    global_emitter.emit('send_skill_start')


def GetFollowUp(timeout_secs=0):
    loop = asyncio.get_event_loop()
    task_return = asyncio.Future()
    task_id = uuid.uuid1()
    status = 0

    def OnResultReceived(msg):
        nonlocal status
        nonlocal task_return

        if status == 0:
            StopTimer(task_id)
            global_emitter.off('follow_up', OnResultReceived)
            loop.call_soon_threadsafe(task_return.set_result, msg)
            global_emitter.emit('stop_follow_up')
            status = 1

    def OnTimeout():
        nonlocal status
        nonlocal task_return
        if status == 0:
            global_emitter.off('follow_up', OnResultReceived)
            loop.call_soon_threadsafe(task_return.set_result, None)
            global_emitter.emit('stop_follow_up')
            status = 1

    global_emitter.on('follow_up', OnResultReceived)

    global_emitter.emit('start_follow_up')
    if timeout_secs > 0:
        StartTimer(timer_id=task_id, length=timeout_secs, callback=OnTimeout)

    return task_return


def DownloadFile(url: str, OnProgress: Callable[[int, int], None] = lambda t, p: None):
    f = BytesIO()
    r = requests.get(url, stream=True)
    total = r.headers["Content-Length"]

    for chunk in r.iter_content(1024):
        f.write(chunk)
        OnProgress(total, f.getbuffer().nbytes)

    return f


async def GetFileHash(dir: str, block_size=65536):
    loop = asyncio.get_event_loop()
    task_return = asyncio.Future()
    file_hash = hashlib.sha256()

    def HashThread():
        with open(dir, 'rb') as f:
            fb = f.read(block_size)
            while len(fb) > 0:
                loop.call_soon_threadsafe(file_hash.update, fb)
                (fb)
                fb = f.read(block_size)
            loop.call_soon_threadsafe(task_return.set_result, file_hash)

    Thread(daemon=True, target=HashThread, group=None).start()

    result = await task_return

    return result
