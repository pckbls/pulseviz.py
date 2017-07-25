import pyglet
from pyglet import gl
import numpy
from . import visualizer, Visualizer, VisualizerWindow
from ..dsp.sampler import Sampler


class WaveformVisualizerWindow(VisualizerWindow):
    def __init__(self, samples_n, **kwargs):
        super().__init__(**kwargs)
        self._samples_n = samples_n
        self._bin_width = 1.0 / samples_n
        self._vertices = numpy.zeros(samples_n * 2)
        self.update_y_values(numpy.zeros(samples_n))

    def update_y_values(self, values, dt=0.0):
        # TOOD: Calculate those in on_resize
        self._vertices[0::2] = numpy.arange(0, self._samples_n) * self._bin_width * self.width
        self._vertices[1::2] = (values / 2.0 + 0.5) * self.height

    def on_draw(self):
        self.clear()
        gl.glColor3f(0.25, 0.0, 1.0)
        pyglet.graphics.draw(self._samples_n,
                             pyglet.gl.GL_LINE_STRIP,
                             ('v2f', self._vertices))
        self.draw_debug_overlay()


@visualizer(name='waveform')
class WaveformVisualizer(Visualizer):
    ANALYZER_TYPE = Sampler
    VISUALIZER_WINDOW_TYPE = WaveformVisualizerWindow
    WINDOW_TITLE = 'Waveform Visualizer'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _update(self, dt):
        with self._analyzer.lock:
            self._window.update_y_values(self._analyzer.buffer, dt)

    def _setup_analyzer(self):
        self._analyzer_kwargs['sample_size'] = 256
        self._analyzer_kwargs['buffer_size'] = 4096
        super()._setup_analyzer()

    def _setup_window(self):
        self._window_kwargs['samples_n'] = self._analyzer.buffer_size
        super()._setup_window()

    def start(self, **kwargs):
        pyglet.clock.schedule_interval(self._update, 1 / 60)
        super().start(**kwargs)
