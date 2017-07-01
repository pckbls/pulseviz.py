import pyglet
from pyglet import gl
from . import visualizer, Visualizer, VisualizerWindow
from ..dsp.sampler import Sampler


class WaveformVisualizerWindow(VisualizerWindow):
    def update(self, dt):
        # TODO: Update vertex data here.
        pass

    def on_draw(self):
        self.clear()

        with self._analyzer.samples_lock:
            bin_width = self.width / self._analyzer.sample_size

            gl.glColor3f(0.25, 0.0, 1.0)
            gl.glBegin(gl.GL_LINE_STRIP)
            for i, height in enumerate(self._analyzer.samples):
                x_min = i * bin_width
                y = self._analyzer.samples[i] * self.height / 2 + self.height / 2
                gl.glVertex3f(x_min, y, 0.0)
            gl.glEnd()

        self.draw_debug_overlay()


@visualizer(name='waveform')
class WaveformVisualizer(Visualizer):
    VISUALIZER_WINDOW_TYPE = WaveformVisualizerWindow
    WINDOW_TITLE = 'Waveform Visualizer'

    def setup_analyzer(self):
        self._analyzer = Sampler(pulseaudio_client=self._pulseaudio_client,
                                 sample_size=4096)

    def start(self, **kwargs):
        pyglet.clock.schedule_interval(self._window.update, 1 / 10)
        super().start(**kwargs)
