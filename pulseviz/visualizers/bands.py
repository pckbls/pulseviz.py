import threading
import numpy
import pyglet
from pyglet import gl
from . import visualizer, Visualizer, VisualizerWindow
from ..dsp import bands


class BandsVisualizerWindow(VisualizerWindow):
    # TODO:
    # Use a shader for rendering and offload some of the calculations into it, this should yield a big
    # performance improvement.

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.y_axis_min = -70
        self.y_axis_max = 0
        self.bars_spacing = 0.005
        self.bars_velocity = 0.0
        self.ticks_velocity = 0.25
        self.draw_ticks = True

        self._lock = threading.Lock()
        self._bars_width = (1.0 - (self._analyzer.n - 1) * self.bars_spacing) / self._analyzer.n
        self._bars_x_min = None
        self._bars_x_max = None
        self._bars_height = numpy.zeros(self._analyzer.n)
        self._ticks_y = numpy.zeros(self._analyzer.n)

    def on_sample(self):
        with self._lock:
            bars_height = numpy.array(self._analyzer.values)

            for i in range(0, self._analyzer.n):
                y = numpy.clip((bars_height[i] - self.y_axis_min) / (self.y_axis_max - self.y_axis_min), 0.001, 1.0)
                self._bars_height[i] = y

    def on_update(self, dt):
        # TODO: Remove this.
        if False:
            if self.bars_velocity > 0.0:
                for i in range(0, self._analyzer.n):
                    y = self._bars_height[i]
                    # Animate the bar movement
                    if y > self._bars_height[i]:
                        self._bars_height[i] = y
                    else:
                        self._bars_height[i] -= self.bars_velocity * dt
                        if self._bars_height[i] < y:
                            self._bars_height[i] = y
            else:
                # Bar animations are disabled
                pass

        with self._lock:
            # Animate the ticks
            for i in range(0, self._analyzer.n):
                self._ticks_y[i] -= self.ticks_velocity * dt
                if self._bars_height[i] > self._ticks_y[i]:
                    self._ticks_y[i] = self._bars_height[i]

    def on_draw_(self):
        with self._lock:
            for i in range(0, self._analyzer.n):
                # TODO: Calculate those in on_resize()
                x_min = (i * self._bars_width + i * self.bars_spacing) * self.width
                x_max = ((i + 1) * self._bars_width + i * self.bars_spacing) * self.width

                if self._bars_height[i] > 0:
                    gl.glBegin(gl.GL_QUADS)
                    gl.glColor3f(1.0, 0.0, 3.0)
                    gl.glVertex3f(x_min, 0.0, 0.0)
                    gl.glVertex3f(x_max, 0.0, 0.0)
                    gl.glColor3f(0.3, 0.0, 1.0)
                    gl.glVertex3f(x_max, self._bars_height[i] * self.height, 0.0)
                    gl.glVertex3f(x_min, self._bars_height[i] * self.height, 0.0)
                    gl.glEnd()

                if self.draw_ticks and self._ticks_y[i] > 0:
                    gl.glLineWidth(2.0)
                    gl.glBegin(gl.GL_LINES)
                    gl.glColor3f(1.0, 1.0, 1.0)
                    gl.glVertex3f(x_min, self._ticks_y[i] * self.height + 2.0, 0.0)
                    gl.glVertex3f(x_max, self._ticks_y[i] * self.height + 2.0, 0.0)
                    gl.glEnd()


@visualizer(name='bands')
class BandsVisualizer(Visualizer):
    ANALYZER_TYPE = bands.Bands
    VISUALIZER_WINDOW_TYPE = BandsVisualizerWindow
    WINDOW_TITLE = 'Octave Bands Visualizer'

    def _setup_analyzer(self):
        self._analyzer_kwargs['sample_frequency'] = 44100
        self._analyzer_kwargs['sample_size'] = 8192
        self._analyzer_kwargs['window_size'] = 1024
        self._analyzer_kwargs['window_overlap'] = 0.5
        self._analyzer_kwargs['window_function'] = 'hanning'
        self._analyzer_kwargs['weighting'] = 'Z'
        self._analyzer_kwargs['band_frequencies'] = bands.calculate_octave_bands(fraction=3)
        super()._setup_analyzer()

    def start(self, **kwargs):
        self._analyzer.on_sample(self._window.on_sample)
        pyglet.clock.schedule_interval(self._window.on_update, 1 / 60)
        super().start(**kwargs)
