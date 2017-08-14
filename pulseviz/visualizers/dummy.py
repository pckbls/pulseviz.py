from . import visualizer, Visualizer
from ..dsp import sampler


@visualizer(name='dummy')
class DummyVisualizer(Visualizer):
    ANALYZER_TYPE = sampler.Sampler
    WINDOW_TITLE = 'Dummy Visualizer'

    def _setup_analyzer(self):
        self._analyzer_kwargs['sample_size'] = 256
        self._analyzer_kwargs['buffer_size'] = 8192*16
        super()._setup_analyzer()
