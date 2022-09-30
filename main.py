import sys, asyncio

if sys.platform == "win32" and (3, 8, 0) <= sys.version_info < (3, 9, 0):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import platform

import events
import wx
from assistant import Assistant
from threads.server import server
from ui import MainWindow
from skills import skill_applications,skill_arithmetic,skill_search,skill_speech,skill_time,skill_window,skill_spotify,skill_schedule
import os

app = wx.App(False)
main = MainWindow()
assistant = Assistant()
app.MainLoop()
