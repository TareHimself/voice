import asyncio
import hashlib
import uuid
from io import BytesIO
import aiohttp
import requests
from threading import Thread
from typing import Callable
from core.events import global_emitter
from core.threads import StartTimer, StopTimer


async def GetNluData(phrase):
    async with aiohttp.ClientSession() as session:
        async with session.get("http://localhost:8097/parse?q={}".format(phrase)) as resp:
            return await resp.json()


def TextToSpeech(msg):
    global_emitter.emit('send_speech_voice', msg)


def DisplayUiMessage(msg):
    global_emitter.emit('send_speech_text', msg, True)


def EndSkill():
    global_emitter.emit('send_skill_end')


def StartSkill():
    global_emitter.emit('send_skill_start')


def GetFollowUp(timeout=0):
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
    if timeout > 0:
        StartTimer(timer_id=task_id, length=timeout, callback=OnTimeout)

    return task_return


def DownloadFile(url: str, OnProgress: Callable[[int, int], None] = lambda t, p: None):
    f = BytesIO()
    r = requests.get(url, stream=True)
    total = r.headers["Content-Length"]

    for chunk in r.iter_content(1024):
        f.write(chunk)
        OnProgress(total, f.getbuffer().nbytes)

    return f



async def GetFileHash(dir:str,block_size=65536):
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
            loop.call_soon_threadsafe(task_return.set_result,file_hash)
    
    Thread(daemon=True,target=HashThread,group=None).start()
    
    result = await task_return

    return result
    

