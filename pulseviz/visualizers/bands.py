import numpy
import pyglet
from pyglet import gl
from . import visualizer, Visualizer, VisualizerWindow
from ..dsp.octave_bands import OctaveBandsAnalayzer


class BandsVisualizerWindow(VisualizerWindow):
    # TODO:
    # Use a shader for rendering and offload some of the calculations into it, this should yield a big
    # performance improvement.

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.y_axis_min = -50
        self.y_axis_max = 50
        self.bars_spacing = 0.005
        self.bars_velocity = 0.0
        self.draw_ticks = True

        self._bars_width = (1.0 - (self._analyzer.n() - 1) * self.bars_spacing) / self._analyzer.n()
        self._bars_x_min = None
        self._bars_x_max = None
        self._bars_height = numpy.zeros(self._analyzer.n())
        self._ticks_y = numpy.zeros(self._analyzer.n())

    def update(self, dt):
        with self._analyzer.bands_lock:
            bars_height = numpy.array(self._analyzer.bands_values)

        for i in range(0, self._analyzer.n()):
            y = numpy.clip((bars_height[i] - self.y_axis_min) / (self.y_axis_max - self.y_axis_min), 0.001, 1.0)

            if self.bars_velocity > 0.0:
                # Animate the bars
                sign = numpy.sign(y - self._bars_height[i])
                if sign == 1.0:
                    self._bars_height[i] += self.bars_velocity * dt
                    if self._bars_height[i] > y:
                        self._bars_height[i] = y
                elif sign == -1.0:
                    self._bars_height[i] -= self.bars_velocity * dt
                    if self._bars_height[i] < y:
                        self._bars_height[i] = y
            else:
                # Bar animations are disabled
                self._bars_height[i] = y

        # Animate the ticks
        for i in range(0, self._analyzer.n()):
            self._ticks_y[i] -= 0.25 * dt
            if self._bars_height[i] > self._ticks_y[i]:
                self._ticks_y[i] = self._bars_height[i]

    def on_draw(self):
        self.clear()

        for i in range(0, self._analyzer.n()):
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

        self.draw_debug_overlay()


@visualizer(name='bands')
class BandsVisualizer(Visualizer):
    VISUALIZER_WINDOW_TYPE = BandsVisualizerWindow
    WINDOW_TITLE = 'Octave Bands Visualizer'

    def setup_analyzer(self, source_name):
        self._analyzer = OctaveBandsAnalayzer(source_name=source_name,
                                              sample_size=4096,
                                              window_function='hanning',
                                              fraction=3)

    def start(self, **kwargs):
        pyglet.clock.schedule_interval(self._window.update, 1 / 60)
        super().start(**kwargs)
