import threading
import numpy as np

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from . import Visualizer
from ..opengl_window import OpenGLWindow2D
from ..dsp.fft import FFTAnalyzer


class SpectrumVisualizer(Visualizer):
    window_name = 'spectrum - pulseviz'

    def __init__(self, sample_size, pulseaudio_client, **kwargs):
        OpenGLWindow2D.__init__(self, **kwargs)  # TODO
        self.analyzer = FFTAnalyzer(sample_size=sample_size,
                                    pulseaudio_client=pulseaudio_client)
        self.auto_scale = True
        self.max_observed_y = None

        self.setup_x_axis('log')
        self.setup_y_axis('log', -70, 70)
    
    def setup_x_axis(self, mode):
        self.x_axis_mode = mode
    
    def setup_y_axis(self, mode, min_y, max_x):
        self.y_axis_mode = mode
        self.y_axis_min = min_y
        self.y_axis_max = max_x

    def _resize(self, width, height):
        super(SpectrumVisualizer, self)._resize(width, height)

        if self.x_axis_mode == 'lin':
            self.x_coordinates = np.linspace(0, self.width, len(self.analyzer.fft))
        elif self.x_axis_mode == 'log':
            self.x_coordinates = (self.width+1) \
                    - np.logspace(np.log2(self.width+1),
                                  0,
                                  len(self.analyzer.fft),
                                  base=2)
        else:
            raise Exception('Unknown option: {0}'.format(self.x_axis_mode))

    def _display(self):
        with self.analyzer.fft_lock:
            if self.y_axis_mode == 'lin':
                y_coordinates = self.analyzer.fft
            elif self.y_axis_mode == 'log':
                # TODO: Fix division-by-zero RuntimeWarnings.
                y_coordinates = 20 * np.log10(self.analyzer.fft)
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

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glColor3f(0.25, 0.0, 1.0)
            glBegin(GL_LINE_STRIP)
            for x, y in zip(self.x_coordinates, y_coordinates):
                glVertex3f(x, y * self.height, 0.0)
            glEnd()
            glutSwapBuffers()
