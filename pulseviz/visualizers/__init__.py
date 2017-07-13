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
    def __init__(self, visualizer, **kwargs):
        super().__init__(**kwargs)

        self.debug_overlay = False

        self._visualizer = visualizer
        self._analyzer = self._visualizer._analyzer  # TODO: We access a private variable here
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
    VISUALIZER_WINDOW_TYPE = VisualizerWindow
    WINDOW_TITLE = '(N/A)'

    def __init__(self, source_name, stop_callback):
        self._stop_callback = stop_callback
        self._analyzer = None
        self.setup_analyzer(source_name)
        self._window = self.VISUALIZER_WINDOW_TYPE(visualizer=self,
                                                   resizable=True,
                                                   caption=self.WINDOW_TITLE + ' - pulseviz.py')

    def setup_analyzer(self, source_name):
        pass

    def start(self):
        # TODO: assert statements will be removed during optimization phase!
        assert isinstance(self._analyzer, PulseAudioSignalAnalayzer)  # TODO: See above ^
        assert isinstance(self._window, VisualizerWindow)  # TODO: See above ^
        self._analyzer.start()

    def stop(self):
        self._analyzer.stop()
        self._analyzer.join()
        self._stop_callback()
