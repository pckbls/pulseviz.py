import threading
import numpy as np

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from . import visualizer
from ..visualizer import Visualizer
from ..opengl_window import OpenGLWindow2D
from ..dsp.fft_bands import FFTBandsAnalayzer


@visualizer(name='bands')
class BandsVisualizer(Visualizer):
    window_name = 'frequency bands - pulseviz'

    def __init__(self, sample_size, pulseaudio_client, **kwargs):
        OpenGLWindow2D.__init__(self, **kwargs)  # TODO
        self.analyzer = FFTBandsAnalayzer(sample_size=sample_size,
                                          pulseaudio_client=pulseaudio_client)
        self.analyzer.set_frequency_bands([
            (0, 50),
            (50, 100),
            (100, 200),
            (200, 400),
            (400, 800),
            (800, 1600),
            (1600, 3200),
            (3200, 6400),
            (6400, 12800),
            (12800, 22050)
        ])
        
        self.frequency_bins = 10
        self.bin_spacing = 5.0
        self.bin_heights = np.linspace(0.0, 1.0, self.frequency_bins)
        self.auto_scale = True
        self.max_observed_y = None

        #self.setup_y_axis('lin', 0, 10)
        self.setup_y_axis('log', -50, 50)
        #self.setup_y_axis('lin', 0, None)
    
    def setup_y_axis(self, mode, min, max):
        self.y_axis_mode = mode
        self.y_axis_min = min
        self.y_axis_max = max

    def _display(self):
        bin_width = (self.width - (self.frequency_bins - 1) * self.bin_spacing) / self.frequency_bins

        with self.analyzer.fft_bands_lock:
            self.bin_heights = self.analyzer.fft_bands

            if self.y_axis_mode == 'lin':
                self.bin_heights = np.array(self.bin_heights)
            elif self.y_axis_mode == 'log':
                self.bin_heights = 20 * np.log10(self.bin_heights)
            else:
                raise Exception('foo')  # TODO

            self.bin_heights = (self.bin_heights - self.y_axis_min) / (self.y_axis_max - self.y_axis_min)

        if False and self.auto_scale:
            m = np.max(self.bin_heights)
            if self.max_observed_y is None or m > self.max_observed_y:
                self.max_observed_y = m
            if self.max_observed_y > 0.0:
                self.bin_heights /= self.max_observed_y

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        for i in range(0, self.frequency_bins):
            x_min = i * bin_width + i * self.bin_spacing
            x_max = (i+1) * bin_width + i * self.bin_spacing
            y = self.bin_heights[i] * self.height

            glBegin(GL_QUADS)
            glColor3f(1.0, 0.0, 3.0)
            glVertex3f(x_min, 0.0, 0.0)
            glVertex3f(x_max, 0.0, 0.0)
            glColor3f(0.3, 0.0, 1.0)
            glVertex3f(x_max, y, 0.0)
            glVertex3f(x_min, y, 0.0)
            glEnd()

        glutSwapBuffers()
