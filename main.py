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
