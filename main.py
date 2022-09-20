
import wx
from ui import MainWindow

from skills import skill_applications,skill_arithmetic,skill_search,skill_speech,skill_time,skill_window

app = wx.App()
main = MainWindow()
main.Show()
app.MainLoop()
