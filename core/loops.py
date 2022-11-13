
import asyncio
from threading import Thread


def create_async_loop() -> asyncio.AbstractEventLoop:
    async_loop = asyncio.new_event_loop()

    def run_loop():
        nonlocal async_loop
        async_loop.run_forever()

    LoopThread = Thread(daemon=True, target=run_loop, group=None)
    LoopThread.start()
    return async_loop
