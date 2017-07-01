import threading
import numpy
from . import PulseAudioSignalAnalayzer


class Sampler(PulseAudioSignalAnalayzer):
    def __init__(self, sample_size, **kwargs):
        super().__init__(**kwargs)

        self.sample_size = sample_size
        self.samples_lock = threading.Lock()
        self.samples = numpy.zeros(self.sample_size, dtype='f')

    def _sample(self):
        samples = self._pulseaudio_client.read_samples(size=self.sample_size)
        with self.samples_lock:
            self.samples = numpy.array(samples, dtype='f')
