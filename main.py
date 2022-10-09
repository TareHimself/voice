import importlib
import sys, asyncio
from os import listdir, path, getcwd

if sys.platform == "win32" and (3, 8, 0) <= sys.version_info < (3, 9, 0):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import wx
from core.assistant import Assistant
from ui import MainWindow

app = wx.App(False)
main = MainWindow()
assistant = Assistant()
app.MainLoop()
