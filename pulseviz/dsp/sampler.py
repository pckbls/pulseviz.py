import threading
import numpy
from . import PulseAudioSignalAnalayzer


class Sampler(PulseAudioSignalAnalayzer):
    """
    Samples the audio signal recorded from the PulseAudio source.
    """

    def __init__(self, sample_size, **kwargs):
        super().__init__(**kwargs)

        self._samples_lock = threading.Lock()
        self._sample_size = sample_size
        self._samples = numpy.zeros(self._sample_size, dtype='f')

    @property
    def lock(self):
        return self._samples_lock

    @property
    def sample_size(self):
        return self._sample_size

    @property
    def samples(self):
        return self._samples

    def _sample(self):
        samples = self._pulseaudio_client.read(size=self._sample_size)
        with self.lock:
            self._samples[:] = samples
