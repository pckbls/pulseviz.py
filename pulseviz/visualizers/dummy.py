from . import visualizer, Visualizer
from ..dsp import PulseAudioSignalAnalayzer


@visualizer(name='dummy')
class DummyVisualizer(Visualizer):
    WINDOW_TITLE = 'Dummy Visualizer'

    def setup_analyzer(self):
        self._analyzer = PulseAudioSignalAnalayzer(pulseaudio_client=self._pulseaudio_client)
