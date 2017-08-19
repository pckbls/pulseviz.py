import pyglet
from ...dsp.sampler import Sampler
from .. import visualizer, Visualizer
from .window import ShadertoyVisualizerWindow


@visualizer(name='shadertoy')
class ShadertoyVisualizer(Visualizer):
    ANALYZER_TYPE = Sampler
    VISUALIZER_WINDOW_TYPE = ShadertoyVisualizerWindow
    WINDOW_TITLE = 'Shadertoy Visualizer'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _setup_analyzer(self):
        self._analyzer_kwargs['sample_size'] = 512
        super()._setup_analyzer()

    def _setup_window(self):
        super()._setup_window()

    def start(self, **kwargs):
        self._analyzer.on_sample(self._window.on_sample)
        pyglet.clock.schedule_interval(self._window.on_update, 1 / 60)
        super().start(**kwargs)