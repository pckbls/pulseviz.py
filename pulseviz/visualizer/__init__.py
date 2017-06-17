from ..opengl_window import OpenGLWindow2D


class Visualizer(OpenGLWindow2D):
    window_name = 'pulseviz'

    def __init__(self, pulseaudio_client, **kwargs):
        super(Visualizer, self).__init__(**kwargs)
        self.analyzer = None

    def run(self):
        self.analyzer.start()
        super(Visualizer, self).run()

    def quit(self):
        super(Visualizer, self).quit()
        self.analyzer.stop()
        self.analyzer.join()
