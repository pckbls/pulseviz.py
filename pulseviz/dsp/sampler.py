import threading
import numpy
from . import PulseAudioSignalAnalayzer


class Sampler(PulseAudioSignalAnalayzer):
    """
    Samples the audio signal recorded from the PulseAudio source.
    """

    def __init__(self, sample_size, **kwargs):
        super().__init__(**kwargs)

        self.samples_lock = threading.Lock()
        self.sample_size = sample_size
        self.samples = numpy.zeros(self.sample_size, dtype='f')

    def _sample(self):
        samples = numpy.array(self._pulseaudio_client.read(size=self.sample_size), dtype='f')
        with self.samples_lock:
            self.samples = samples
