from . import visualizer, Visualizer
from ..dsp.sampler import Sampler


@visualizer(name='dummy')
class DummyVisualizer(Visualizer):
    ANALYZER_TYPE = Sampler
    WINDOW_TITLE = 'Dummy Visualizer'

    def _setup_analyzer(self):
        self._analyzer_kwargs['sample_size'] = 256
        self._analyzer_kwargs['buffer_size'] = 4096
        super()._setup_analyzer()
