import wx
from constants import main_window_name, wx_color_darkgrey, wake_word
from events import global_emitter
from ui.visualizer import Visualizer
from skills import GetCommand


class MainWindow(wx.Frame):

    def __init__(self):
        super(MainWindow, self).__init__(None, title=main_window_name, size=(int(1920 / 2), int(1080 / 2)))
        self.vis = Visualizer(self, bar_width=7, channels=20)
        self.SetBackgroundColour(wx_color_darkgrey)
        global_emitter.on('window_action', self.DoWindowAction)
        self.Show()

    def DoWindowAction(self, action: str):
        if action == "maximize":
            self.Maximize()
        elif action == "minimize":
            self.Iconize()
        elif action == "restore":
            self.Restore()
