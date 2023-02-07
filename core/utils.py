import asyncio
import hashlib
import uuid
from io import BytesIO
import aiohttp
import requests
from threading import Thread
from typing import Callable, Union
from core.events import GLOBAL_EMITTER
from core.logger import log
from core.threads import start_timer, stop_timer
from core import constants
from core.decorators import get_singleton
from core.assistant import AssistantContext


async def parse_phrase(phrase):
    parser = get_singleton(constants.SINGLETON_INTENTS_INFERENCE_ID)

    return parser.get_intent(phrase)


def display_ui_message(msg):
    GLOBAL_EMITTER.emit('send_speech_text', msg, True)


def end_skill():
    GLOBAL_EMITTER.emit(constants.EVENT_ON_SKILL_END)


def start_skill():
    GLOBAL_EMITTER.emit(constants.EVENT_ON_SKILL_START)


def download_file(url: str, OnProgress: Callable[[int, int], None] = lambda t, p: None):
    f = BytesIO()
    r = requests.get(url, stream=True)
    total = r.headers["Content-Length"]

    for chunk in r.iter_content(1024):
        f.write(chunk)
        OnProgress(total, f.getbuffer().nbytes)

    return f


async def get_file_hash(dir: str, block_size=65536):
    loop = asyncio.get_event_loop()
    task_return = asyncio.Future()
    file_hash = hashlib.sha256()

    def hash_thread():
        with open(dir, 'rb') as f:
            fb = f.read(block_size)
            while len(fb) > 0:
                loop.call_soon_threadsafe(file_hash.update, fb)
                (fb)
                fb = f.read(block_size)
            loop.call_soon_threadsafe(task_return.set_result, file_hash)

    Thread(daemon=True, target=hash_thread, group=None).start()

    result = await task_return

    return result


async def try_start_skill(phrase, response_handler=AssistantContext, *args) -> list:
    assistant = get_singleton(constants.SINGLETON_ASSISTANT_ID)
    return await assistant.try_start_skill(phrase, response_handler, *args)


def run_in_thread(func, *args: list):
    Thread(target=func, daemon=True, group=None, args=args).start()


def hash_string(string: str):
    return hashlib.md5(string.encode()).hexdigest()
