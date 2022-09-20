import platform

import wx

from threads.server import StartServer
from ui import MainWindow
from skills import skill_applications,skill_arithmetic,skill_search,skill_speech,skill_time,skill_window


s = StartServer()

app = wx.App()
main = MainWindow()
main.Show()
app.MainLoop()
