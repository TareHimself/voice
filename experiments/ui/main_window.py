from os import getcwd, path
import wx
from core.constants_1 import main_window_name, dynamic
from core.events import gEmitter
from ui.visualizer import Visualizer
from wx.html2 import WebView as WV


class MainWindow(wx.Frame):

    def __init__(self):
        super(MainWindow, self).__init__(
            None, title=main_window_name, size=(int(1920 / 2), int(1080 / 2)))
        #self.vis = Visualizer(self, bar_width=7, channels=20)
        self.WebView = WV.New(self)
        self.WebView.LoadURL("https://umeko.dev/")
        self.SetBackgroundColour(dynamic.wx_color_darkgrey)
        gEmitter.on('window_action', self.DoWindowAction)
        self.Show()
        self.SetIcon(wx.Icon(path.join(getcwd(), 'assets', 'icon.png')))

    def DoWindowAction(self, action: str):
        if action == "maximize":
            self.Maximize()
        elif action == "minimize":
            self.Iconize()
        elif action == "restore":
            self.Restore()
