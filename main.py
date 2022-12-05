import sys
import asyncio
if sys.platform == "win32" and (3, 8, 0) <= sys.version_info < (3, 9, 0):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
import signal
import time

from core.threads import StartServer
from core.events import gEmitter
from core.assistant import Assistant
import os

d = os.path.join
os.path.join = lambda *args, **kwargs: os.path.normpath(d(*args, *kwargs))
assistant = Assistant()
StartServer()

#import wx


def on_process_end(sig, frame):
    gEmitter.emit('terminate', sig, frame)
    sys.exit(sig)


signal.signal(signal.SIGINT, on_process_end)

try:
    while True:
        time.sleep(100)
except KeyboardInterrupt:
    pass

# app = wx.App()
# MainWindow()
# app.MainLoop()
