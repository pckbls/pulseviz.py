import pyglet
from ..dsp import PulseAudioSignalAnalayzer


registry = {}


def visualizer(name):
    def _wrap(cls):
        registry[name] = cls
        return cls
    return _wrap


class VisualizerWindow(pyglet.window.Window):
    def __init__(self, visualizer, **kwargs):
        super().__init__(**kwargs)

        self._visualizer = visualizer
        self._analyzer = self._visualizer._analyzer  # TODO: We access a private variable here

    def on_draw(self):
        self.clear()

    def on_key_press(self, symbol, modifiers):
        if symbol == ord('q'):
            self._visualizer.stop()


class Visualizer(object):
    VISUALIZER_WINDOW_TYPE = VisualizerWindow
    WINDOW_TITLE = '(N/A)'

    def __init__(self, pulseaudio_client):
        self._pulseaudio_client = pulseaudio_client
        self._analyzer = None
        self.setup_analyzer()
        self._window = self.VISUALIZER_WINDOW_TYPE(visualizer=self,
                                                   resizable=False,
                                                   caption=self.WINDOW_TITLE + ' - pulseviz.py')

    def setup_analyzer(self):
        pass

    def start(self):
        assert isinstance(self._analyzer, PulseAudioSignalAnalayzer)
        assert isinstance(self._window, VisualizerWindow)
        self._analyzer.start()
        pyglet.app.run()

    def stop(self):
        pyglet.app.exit()
        self._analyzer.stop()
        self._analyzer.join()
