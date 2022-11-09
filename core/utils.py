import asyncio
import hashlib
import uuid
from io import BytesIO
import aiohttp
import requests
from threading import Thread
from typing import Callable, Union
from core.events import gEmitter
from core.logger import log
from core.threads import StartTimer, StopTimer
from core import constants


async def GetNluData(phrase):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://proxy.oyintare.dev/nlu/parse?q={}".format(phrase)) as resp:
                nlu_response = await resp.json()
                log(nlu_response)
                if len(nlu_response['error']):
                    return None

                return [nlu_response['data']['intent']['name'], nlu_response['data']['intent']['confidence']]
    except aiohttp.ClientConnectorError as e:
        log(e)
        return None


def DisplayUiMessage(msg):
    log(msg)
    gEmitter.emit('send_speech_text', msg, True)


def EndSkill():
    gEmitter.emit(constants.EVENT_ON_SKILL_END)


def StartSkill():
    gEmitter.emit(constants.EVENT_ON_SKILL_START)


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
            gEmitter.off(constants.EVENT_ON_FOLLOWUP_MSG, OnResultReceived)
            loop.call_soon_threadsafe(task_return.set_result, msg)
            gEmitter.emit(constants.EVENT_ON_FOLLOWUP_END)
            status = 1

    def OnTimeout():
        nonlocal status
        nonlocal task_return
        if status == 0:
            gEmitter.off(constants.EVENT_ON_FOLLOWUP_MSG, OnResultReceived)
            loop.call_soon_threadsafe(task_return.set_result, None)
            gEmitter.emit(constants.EVENT_ON_FOLLOWUP_END)
            status = 1

    gEmitter.on(constants.EVENT_ON_FOLLOWUP_MSG, OnResultReceived)

    gEmitter.emit(constants.EVENT_ON_FOLLOWUP_START)
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
