import numpy
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from . import visualizer
from ..visualizer import Visualizer
from ..dsp.fft_bands import FFTBandsAnalayzer


@visualizer(name='bands')
class BandsVisualizer(Visualizer):
    window_name = 'frequency bands - pulseviz'

    def __init__(self, sample_size, pulseaudio_client, **kwargs):
        super(BandsVisualizer, self).__init__(**kwargs)
        # TODO: Remove this, once we can configure pulseviz properly.
        # Override both sample size and refresh rate for this visualizer.
        self.refresh_rate = 30.0
        self.sample_size = 4096

        self.analyzer = FFTBandsAnalayzer(sample_size=sample_size,
                                          pulseaudio_client=pulseaudio_client)
        self.analyzer.generate_octave_bands(fraction=3)

        self.y_axis_min = -50
        self.y_axis_max = 50

        self.bar_spacing = 0.01
        self.bar_width = (1.0 - (self.analyzer.n() - 1) * self.bar_spacing) / self.analyzer.n()

        self._ticks_y = self.y_axis_min * numpy.ones(self.analyzer.n())

    def _display(self):
        with self.analyzer.fft_bands_lock:
            bar_heights = numpy.array(self.analyzer.fft_bands)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for i in range(0, self.analyzer.n()):
            x_min = (i * self.bar_width + i * self.bar_spacing) * self.width
            x_max = ((i + 1) * self.bar_width + i * self.bar_spacing) * self.width
            y = ((bar_heights[i] - self.y_axis_min) / (self.y_axis_max - self.y_axis_min))

            if y > self._ticks_y[i]:
                self._ticks_y[i] = y
            else:
                self._ticks_y[i] -= 0.005

            glBegin(GL_QUADS)
            glColor3f(1.0, 0.0, 3.0)
            glVertex3f(x_min, 0.0, 0.0)
            glVertex3f(x_max, 0.0, 0.0)
            glColor3f(0.3, 0.0, 1.0)
            glVertex3f(x_max, y * self.height, 0.0)
            glVertex3f(x_min, y * self.height, 0.0)
            glEnd()

            glLineWidth(2.0)
            glBegin(GL_LINES)
            glColor3f(1.0, 1.0, 1.0)
            glVertex3f(x_min, self._ticks_y[i] * self.height + 2.0, 0.0)
            glVertex3f(x_max, self._ticks_y[i] * self.height + 2.0, 0.0)
            glEnd()
        glutSwapBuffers()
