import numpy as np
from wx.html2 import WebView as WV
from core.constants import dynamic
from core.events import global_emitter
from core.threads import StartFFT

SMOOTHING_RATE = 7


class WebView(WV):

    def __init__(self, parent):
        super(WebView, self).__init__(parent)
        self.LoadURL('https://umeko.dev/')
