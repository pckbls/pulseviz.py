import threading
import pyglet
from pyglet import gl
import numpy
from . import visualizer, Visualizer, VisualizerWindow
from ..dsp.sampler import Sampler


class WaveformVisualizerWindow(VisualizerWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._samples_n = self._analyzer.buffer_size
        self._vertex_list = pyglet.graphics.vertex_list(
            self._samples_n,
            ('v2f/dynamic', numpy.zeros(self._samples_n * 2))
        )
        self._lock = threading.Lock()

    def on_sample(self):
        with self._lock:
            self._vertex_list.vertices[1::2] = (self._analyzer.buffer / 2.0 + 0.5) * self.height

    def on_update(self, dt):
        pass

    def on_resize(self, width, height):
        super().on_resize(width, height)
        with self._lock:
            bin_width = 1.0 / self._samples_n
            self._vertex_list.vertices[0::2] = numpy.arange(0, self._samples_n) * bin_width * self.width

    def on_draw_(self):
        gl.glColor3f(0.25, 0.0, 1.0)
        with self._lock:
            self._vertex_list.draw(pyglet.gl.GL_LINE_STRIP)


@visualizer(name='waveform')
class WaveformVisualizer(Visualizer):
    ANALYZER_TYPE = Sampler
    VISUALIZER_WINDOW_TYPE = WaveformVisualizerWindow
    WINDOW_TITLE = 'Waveform Visualizer'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _setup_analyzer(self):
        self._analyzer_kwargs['sample_size'] = 512
        self._analyzer_kwargs['buffer_size'] = 512 * 32
        super()._setup_analyzer()

    def _setup_window(self):
        super()._setup_window()

    def start(self, **kwargs):
        self._analyzer.on_sample(self._window.on_sample)
        pyglet.clock.schedule_interval(self._window.on_update, 1 / 60)
        super().start(**kwargs)
