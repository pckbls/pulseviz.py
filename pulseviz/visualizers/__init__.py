from ..opengl_window import OpenGLWindow2D


visualizers = {}


def visualizer(name):
    def _wrap(cls):
        visualizers[name] = cls
        return cls
    return _wrap


class Visualizer(OpenGLWindow2D):
    window_name = 'pulseviz'

    def __init__(self, **kwargs):
        super(Visualizer, self).__init__(**kwargs)
        self.analyzer = None

    def run(self):
        self.analyzer.start()
        super(Visualizer, self).run()

    def quit(self):
        super(Visualizer, self).quit()
        self.analyzer.stop()
        self.analyzer.join()


# TODO: Is there any way to remove this?
from . import waveform, spectrum, bands
