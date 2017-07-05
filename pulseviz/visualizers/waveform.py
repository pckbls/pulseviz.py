import pyglet
from pyglet import gl
import numpy
from . import visualizer, Visualizer, VisualizerWindow
from ..dsp.sampler import Sampler


class WaveformVisualizerWindow(VisualizerWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._y_values = numpy.zeros(self._analyzer.sample_size)
        self._bin_width = 1.0 / self._analyzer.sample_size

    def update(self, dt):
        with self._analyzer.samples_lock:
            self._y_values = self._analyzer.samples / 2.0 + 0.5

    def on_draw(self):
        self.clear()

        gl.glColor3f(0.25, 0.0, 1.0)
        gl.glBegin(gl.GL_LINE_STRIP)
        for i in range(0, self._analyzer.sample_size):
            gl.glVertex3f(i * self._bin_width * self.width, self._y_values[i] * self.height, 0.0)
        gl.glEnd()

        self.draw_debug_overlay()


@visualizer(name='waveform')
class WaveformVisualizer(Visualizer):
    VISUALIZER_WINDOW_TYPE = WaveformVisualizerWindow
    WINDOW_TITLE = 'Waveform Visualizer'

    def setup_analyzer(self, source_name):
        self._analyzer = Sampler(source_name=source_name,
                                 sample_size=2048)

    def start(self, **kwargs):
        pyglet.clock.schedule_interval(self._window.update, 1 / 10)
        super().start(**kwargs)
