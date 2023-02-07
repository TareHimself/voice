import numpy as np
import wx
from core.constants_1 import dynamic
from core.events import GLOBAL_EMITTER
from core.threads import StartFFT

SMOOTHING_RATE = 7


class Visualizer(wx.Panel):

    def __init__(self, parent, channels=16, bar_width=20):
        super(Visualizer, self).__init__(parent)
        self.channels = channels
        self.bar_width = bar_width
        self.Bind(wx.PyEventBinder(wx.wxEVT_PAINT, 1), self.OnPaint)
        self.SetSize(parent.GetSize())
        self.fft_data = [bar_width for element in range(channels)]
        self.fft_smooth_data = [bar_width for element in range(channels)]
        self.voice_inst = StartFFT(
            callback=self.OnVoiceData, channels=channels)
        self.SetDoubleBuffered(True)
        self.timer = wx.Timer(self, wx.ID_ANY)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        self.timer.Start(15, wx.TIMER_CONTINUOUS)
        self.status_text = "Starting Up Speech Recognition.."
        GLOBAL_EMITTER.on('send_speech_text', self.UpdatePhrase)

    def OnTimer(self, event):
        for index in range(len(self.fft_data)):
            self.fft_smooth_data[index] += (self.fft_data[index] - self.fft_smooth_data[index]) * (
                self.timer.GetInterval() / 1000) * SMOOTHING_RATE
        self.Refresh()

    def OnVoiceData(self, d):
        def scale(item):
            return min(max(np.interp(item, (0, 4000), (0, self.GetSize()[1] * 0.6)), self.bar_width),
                       self.GetSize()[1] * 0.6)

        if len(d) != self.channels:
            raise Exception(
                "Data sent to 'Visualize' has incorrect channels, expected", self.channels, " got ", len(d))
        for x in range(len(d)):
            self.fft_data[x] = scale(d[x])

    def DrawBar(self, gc, x, y, w, h, radius):
        gc.DrawRoundedRectangle(
            (int(x - (w / 2)), int(y - (h / 2))), (int(w), int(h)), radius)

    def UpdatePhrase(self, phrase, is_complete):
        self.status_text = phrase

    def OnPaint(self, event):

        pdc = wx.PaintDC(self)
        gc = wx.GCDC(pdc)
        gc.SetPen(wx.Pen(dynamic.wx_visualizer_band_color, 2))
        gc.SetBrush(wx.Brush(dynamic.wx_visualizer_band_color))
        size = self.GetSize()
        desired_size = max(500, (self.channels * 6) * self.bar_width)
        padding = (size[0] - (size[0] * (desired_size / size[0]))
                   ) / 2 if desired_size / size[0] < 1 else 1
        start_x = ((size[0] - (padding * 2)) / self.channels)
        for channel in range(self.channels):
            self.DrawBar(gc, padding + (start_x * channel) + start_x * 0.5, size[1] / 2, self.bar_width,
                         self.fft_smooth_data[channel], self.bar_width / 2)

        text_to_draw = self.status_text
        gc.SetFont(wx.Font(15, wx.DEFAULT, wx.NORMAL,
                   wx.NORMAL, False, "Arial"))
        gc.SetTextForeground(dynamic.wx_visualizer_band_color)
        w, h = gc.GetTextExtent(text_to_draw)
        gc.DrawText(
            text_to_draw, (int((size[0] * 0.5) - (0.5 * w)), int((size[1] * 0.8) + h)))
