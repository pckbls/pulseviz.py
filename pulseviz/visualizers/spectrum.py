import numpy as np
import pyglet
from pyglet import gl
from . import visualizer, Visualizer, VisualizerWindow
from ..dsp.fft import FFT


class SpectrumVisualizerWindow(VisualizerWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auto_scale = True
        self.max_observed_y = None

        self.setup_x_axis('log')
        self.setup_y_axis('log', -120, 0)

    def setup_x_axis(self, mode):
        self.x_axis_mode = mode

    def setup_y_axis(self, mode, min_y, max_x):
        self.y_axis_mode = mode
        self.y_axis_min = min_y
        self.y_axis_max = max_x

    def update(self, dt):
        # TODO: Update vertex data here.
        pass

    def on_resize(self, width, height):
        super().on_resize(width, height)

        if self.x_axis_mode == 'lin':
            self.x_coordinates = np.linspace(0, self.width, len(self._analyzer.values))
        elif self.x_axis_mode == 'log':
            self.x_coordinates = self.width + 1
            self.x_coordinates -= np.logspace(np.log2(self.width + 1),
                                              0,
                                              len(self._analyzer.values),
                                              base=2)
        else:
            raise Exception('Unknown option: {0}'.format(self.x_axis_mode))

    def on_draw(self):
        self.clear()

        with self._analyzer.lock:
            if self.y_axis_mode == 'lin':
                y_coordinates = self._analyzer.values
            elif self.y_axis_mode == 'log':
                # TODO: Fix division-by-zero RuntimeWarnings.
                y_coordinates = 20 * np.log10(self._analyzer.values)
            else:
                raise Exception('Unknown option: {0}'.format(self.x_axis_mode))

            y_coordinates = (y_coordinates - self.y_axis_min) / (self.y_axis_max - self.y_axis_min)

            # TODO: Re-implement this properly.
            if False:
                if self.auto_scale:
                    m = np.max(y_coordinates)
                    if self.max_observed_y is None or m > self.max_observed_y:
                        self.max_observed_y = m
                    if self.max_observed_y > 0.0:
                        y_coordinates /= self.max_observed_y

            gl.glColor3f(0.25, 0.0, 1.0)
            gl.glBegin(gl.GL_LINE_STRIP)
            for x, y in zip(self.x_coordinates, y_coordinates):
                gl.glVertex3f(x, y * self.height, 0.0)
            gl.glEnd()

        self.draw_debug_overlay()


@visualizer(name='spectrum')
class SpectrumVisualizer(Visualizer):
    VISUALIZER_WINDOW_TYPE = SpectrumVisualizerWindow
    WINDOW_TITLE = 'Spectrum Visualizer'

    def setup_analyzer(self, source_name):
        self._analyzer = FFT(source_name=source_name,
                             sample_size=4096)

    def start(self, **kwargs):
        pyglet.clock.schedule_interval(self._window.update, 1 / 10)
        super().start(**kwargs)
