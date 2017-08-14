import pyglet
from ..dsp import PulseAudioSignalAnalayzer
from .. import __version__


registry = {}


def visualizer(name):
    def _wrap(cls):
        registry[name] = cls
        return cls
    return _wrap


class DebugOverlayDisplay(pyglet.window.FPSDisplay):
    """
    Displays both FPS and the latency reported by the PulseAudio server.
    """

    def __init__(self, analyzer, window):
        super().__init__(window)

        self._analyzer = analyzer

        self.label.font_size = 14
        self.label.color = (255, 255, 255, 255)
        self.label.font_name = 'monospace'

    def set_fps(self, fps):
        self.label.text = 'FPS: {0:.0f}, PulseAudio Latency: {1:.0f}'.format(
            fps,
            self._analyzer.get_latency()
        )


class VisualizerWindow(pyglet.window.Window):
    HELP_TEXT = '''
    pulseviz {0}

    Available keyboard shortcuts:
    [f] Toggles fullscreen mode
    [h] Toggles this help text
    [d] Toggles the debug overlay
    [q] Quits the application
    '''.format(__version__)

    def __init__(self, visualizer, analyzer, **kwargs):
        super().__init__(**kwargs)

        self._visualizer = visualizer
        self._analyzer = analyzer

        self._show_debug_overlay = False
        self._show_help_text = False

        self._fps_display = DebugOverlayDisplay(self._analyzer, self)

        self._help_text_label = pyglet.text.Label(
            self.HELP_TEXT,
            font_name='monospace',
            font_size=14,
            bold=True,
            x=self.width // 2, y=self.height // 2,
            anchor_x='center', anchor_y='center',
            width=self.width,
            multiline=True
        )

    def on_draw(self):
        self.clear()

        self.on_draw_()

        if self._show_debug_overlay:
            self._fps_display.draw()

        if self._show_help_text:
            self._help_text_label.draw()

    def on_draw_(self):
        pass

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self._help_text_label.x = self.width // 2
        self._help_text_label.y = self.height // 2
        self._help_text_label.width = self.width

    def on_key_press(self, symbol, modifiers):
        if symbol == ord('q'):
            self.on_close()
        elif symbol == ord('f'):
            self.set_fullscreen(not self.fullscreen)
        elif symbol == ord('d'):
            self._show_debug_overlay = not self._show_debug_overlay
        elif symbol == ord('h'):
            self._show_help_text = not self._show_help_text

    def on_close(self):
        self._visualizer.stop()


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
