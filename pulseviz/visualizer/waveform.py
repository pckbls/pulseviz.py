import threading
import numpy as np

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from . import Visualizer
from ..opengl_window import OpenGLWindow2D
from ..dsp.sampler import Sampler


class WaveformVisualizer(Visualizer):
    window_name = 'waveform - pulseviz'

    def __init__(self, sample_size, pulseaudio_client, **kwargs):
        OpenGLWindow2D.__init__(self, **kwargs)  # TODO
        self.analyzer = Sampler(sample_size=sample_size, pulseaudio_client=pulseaudio_client)

    def _display(self):
        with self.analyzer.samples_lock:
            bin_width = self.width / self.analyzer.sample_size

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glColor3f(0.25, 0.0, 1.0)

            glBegin(GL_LINE_STRIP)
            for i, height in enumerate(self.analyzer.samples):
                x_min = i * bin_width
                y = self.analyzer.samples[i] * self.height/2 + self.height/2
                glVertex3f(x_min, y, 0.0)
            glEnd()

            glutSwapBuffers()
