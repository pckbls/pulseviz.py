import numpy
import pyglet
from pyglet import gl
from . import visualizer, Visualizer, VisualizerWindow
from ..dsp.fft import FFT


class SpectrumVisualizerWindow(VisualizerWindow):
    def __init__(self, fft_size, y_lim, **kwargs):
        super().__init__(**kwargs)
        self._fft_size = fft_size
        self._vertices = -numpy.inf * numpy.ones(fft_size * 2)
        self._y_lim = y_lim

    def update(self, values, dt):
        self._vertices[1::2] = (values - self._y_lim[0]) / (self._y_lim[1] - self._y_lim[0]) * self.height

    def on_resize(self, width, height):
        super().on_resize(width, height)

        self._vertices[0::2] = self.width + 1
        self._vertices[0::2] -= numpy.logspace(numpy.log2(self.width + 1),
                                               0,
                                               self._fft_size,
                                               base=2)

    def on_draw(self):
        self.clear()
        gl.glColor3f(0.25, 0.0, 1.0)
        pyglet.graphics.draw(self._fft_size,
                             pyglet.gl.GL_LINE_STRIP,
                             ('v2f', self._vertices))
        self.draw_debug_overlay()


@visualizer(name='spectrum')
class SpectrumVisualizer(Visualizer):
    ANALYZER_TYPE = FFT
    VISUALIZER_WINDOW_TYPE = SpectrumVisualizerWindow
    WINDOW_TITLE = 'Spectrum Visualizer'

    def _setup_analyzer(self):
        self._analyzer_kwargs['sample_frequency'] = 44100
        self._analyzer_kwargs['sample_size'] = 256
        self._analyzer_kwargs['buffer_size'] = 4096
        self._analyzer_kwargs['window_function'] = 'hanning'
        self._analyzer_kwargs['output'] = 'psd'
        self._analyzer_kwargs['scaling'] = 'log'
        super()._setup_analyzer()

    def _setup_window(self):
        self._window_kwargs['fft_size'] = len(self._analyzer.values)
        self._window_kwargs['y_lim'] = (-120.0, 0.0)
        super()._setup_window()

    def _update(self, dt):
        with self._analyzer.lock:
            self._window.update(self._analyzer.values, dt)

    def start(self, **kwargs):
        pyglet.clock.schedule_interval(self._update, 1 / 60)
        super().start(**kwargs)
