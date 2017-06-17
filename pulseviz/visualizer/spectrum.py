import threading
import numpy as np

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from . import Visualizer
from ..opengl_window import OpenGLWindow2D
from ..dsp.spectrum_analyzer import SpectrumAnalayzer


class SpectrumVisualizer(Visualizer):
    window_name = 'spectrum - pulseviz'

    def __init__(self, sample_size, pulseaudio_client, **kwargs):
        OpenGLWindow2D.__init__(self, **kwargs)  # TODO
        self.analyzer = SpectrumAnalayzer(sample_size=sample_size,
                                          pulseaudio_client=pulseaudio_client)
        self.auto_scale = True
        self.max_observed_y = None

    def resize(self, width, height):
        super(SpectrumVisualizer, self).resize(width, height)
        self.x_coordinates = (self.width+1) - np.logspace(np.log2(self.width+1),
                                                          0,
                                                          len(self.analyzer.fft_left_side),
                                                          base=2)

    def display(self):
        with self.analyzer.fft_left_side_lock:
            y_coordinates = self.analyzer.fft_left_side

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
