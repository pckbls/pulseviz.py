from . import visualizer, Visualizer
from ..dsp.sampler import Sampler


@visualizer(name='dummy')
class DummyVisualizer(Visualizer):
    WINDOW_TITLE = 'Dummy Visualizer'

    def setup_analyzer(self, source_name):
        self._analyzer = Sampler(source_name=source_name,
                                 sample_size=2048)
