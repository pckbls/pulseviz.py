import pyglet
from ..dsp import PulseAudioSignalAnalayzer


# TODO: Create new class based on pyglet.window.FPSDisplay and make it draw both FPS and the PulseAudio client latency.

registry = {}


def visualizer(name):
    def _wrap(cls):
        registry[name] = cls
        return cls
    return _wrap


class VisualizerWindow(pyglet.window.Window):
    def __init__(self, visualizer, analyzer=None, **kwargs):
        super().__init__(**kwargs)

        self.debug_overlay = False

        self._visualizer = visualizer
        self._fps_display = pyglet.window.FPSDisplay(self)

    def on_draw(self):
        self.clear()
        self.draw_debug_overlay()

    def on_key_press(self, symbol, modifiers):
        if symbol == ord('q'):
            self.on_close()
        elif symbol == ord('f'):
            self.set_fullscreen(not self.fullscreen)
        elif symbol == ord('d'):
            self.debug_overlay = not self.debug_overlay

    def on_close(self):
        self._visualizer.stop()

    def draw_debug_overlay(self):
        if self.debug_overlay:
            self._fps_display.draw()


class Visualizer(object):
    ANALYZER_TYPE = PulseAudioSignalAnalayzer
    VISUALIZER_WINDOW_TYPE = VisualizerWindow
    WINDOW_TITLE = '(N/A)'

    def __init__(self, source_name, stop_callback):
        self._stop_callback = stop_callback

        self._analyzer_kwargs = {
            'source_name': source_name
        }
        self._analyzer = None
        self._setup_analyzer()

        self._window_kwargs = {
            'visualizer': self,
            'resizable': True,
            'caption': self.WINDOW_TITLE + ' - pulseviz'
        }
        self._window = None
        self._setup_window()

    def _setup_analyzer(self):
        self._analyzer = self.ANALYZER_TYPE(**self._analyzer_kwargs)

    def _setup_window(self):
        self._window_kwargs['analyzer'] = self._analyzer
        self._window = self.VISUALIZER_WINDOW_TYPE(**self._window_kwargs)

    def start(self):
        self._analyzer.start()

    def stop(self):
        self._analyzer.stop()
        self._analyzer.join()
        self._stop_callback()
