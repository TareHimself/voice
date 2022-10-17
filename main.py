import importlib
import sys
import asyncio
from os import listdir, path, getcwd
import time
import wx
from core.threads import StartServer
from ui.main_window import MainWindow
if sys.platform == "win32" and (3, 8, 0) <= sys.version_info < (3, 9, 0):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


from core.assistant import Assistant
assistant = Assistant()
StartServer()
while True:
    time.sleep(100)

# app = wx.App()
# MainWindow()
# app.MainLoop()
