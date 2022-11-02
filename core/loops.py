
import asyncio
from threading import Thread


def CreateAsyncLoop() -> asyncio.AbstractEventLoop:
    async_loop = asyncio.new_event_loop()

    def RunLoop():
        async_loop.run_forever()

    LoopThread = Thread(daemon=True, target=RunLoop, group=None)
    LoopThread.start()
    return async_loop