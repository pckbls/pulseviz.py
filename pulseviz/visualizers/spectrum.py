import threading
import numpy
import pyglet
from pyglet import gl
from . import visualizer, Visualizer, VisualizerWindow
from ..dsp.fft import FFT


class SpectrumVisualizerWindow(VisualizerWindow):
    def __init__(self, y_lim, **kwargs):
        super().__init__(**kwargs)
        self._fft_size = len(self._analyzer.values)
        self._frequencies = self._analyzer.frequencies

        self._vertex_list = pyglet.graphics.vertex_list(
            self._fft_size,
            ('v2f/dynamic', -numpy.inf * numpy.ones(self._fft_size * 2))
        )
        self._lock = threading.Lock()

        self._y_lim = y_lim
        self._x_lim = (10, self._frequencies[-1])

        self._x_coordinates = numpy.array([
            (numpy.log10(freq + 1) - numpy.log10(self._x_lim[0]))
            / (numpy.log10(self._x_lim[1] + 1) - numpy.log10(self._x_lim[0]))
            for freq in self._frequencies
        ])

    def on_sample(self):
        with self._lock:
            values = self._analyzer.values
            self._vertex_list.vertices[1::2] = (values - self._y_lim[0]) \
                / (self._y_lim[1] - self._y_lim[0]) * self.height

    def on_update(self, dt):
        pass

    def on_resize(self, width, height):
        super().on_resize(width, height)
        with self._lock:
            self._vertex_list.vertices[0::2] = self.width * self._x_coordinates

    def on_draw_(self):
        # self._draw_grid()
        gl.glColor3f(0.25, 0.0, 1.0)
        with self._lock:
            self._vertex_list.draw(pyglet.gl.GL_LINE_STRIP)

    def _draw_grid(self):
        gl.glColor3f(0.1, 0.1, 0.1)
        gl.glBegin(gl.GL_LINES)
        for freq in [10, 20, 30, 40, 50, 60, 70, 80, 90,
                     100, 200, 300, 400, 500, 600, 700, 800, 900,
                     1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000,
                     10000, 20000]:
            x = (numpy.log10(freq) - numpy.log10(self._x_lim[0])) \
                    / (numpy.log10(self._x_lim[1]) - numpy.log10(self._x_lim[0]))
            gl.glVertex2f(x * self.width, 0.0 * self.height)
            gl.glVertex2f(x * self.width, 1.0 * self.height)
        gl.glEnd()


@visualizer(name='spectrum')
class SpectrumVisualizer(Visualizer):
    ANALYZER_TYPE = FFT
    VISUALIZER_WINDOW_TYPE = SpectrumVisualizerWindow
    WINDOW_TITLE = 'Spectrum Visualizer'

    def _setup_analyzer(self):
        self._analyzer_kwargs['sample_frequency'] = 44100
        self._analyzer_kwargs['sample_size'] = 8192
        self._analyzer_kwargs['window_size'] = 1024
        self._analyzer_kwargs['window_overlap'] = 0.5
        self._analyzer_kwargs['window_function'] = 'hanning'
        self._analyzer_kwargs['weighting'] = 'Z'
        self._analyzer_kwargs['output'] = 'psd'
        self._analyzer_kwargs['scaling'] = 'log'
        super()._setup_analyzer()

    def _setup_window(self):
        self._window_kwargs['y_lim'] = (-120.0, 0.0)
        super()._setup_window()

    def start(self, **kwargs):
        self._analyzer.on_sample(self._window.on_sample)
        pyglet.clock.schedule_interval(self._window.on_update, 1 / 60)
        super().start(**kwargs)
