import threading
import numpy
from . import PulseAudioSignalAnalayzer
from .. import PulsevizException


class Sampler(PulseAudioSignalAnalayzer):
    """
    Samples the audio signal recorded from the PulseAudio source
    and optionally appends the samples to a fixed-size buffer.
    """

    def __init__(self, sample_size, buffer_size=None, **kwargs):
        super().__init__(**kwargs)

        self._samples_lock = threading.Lock()
        self._samples = numpy.zeros(sample_size, dtype='f')

        if buffer_size is None:
            self._buffer = None
        elif buffer_size >= sample_size:
            self._buffer = numpy.zeros(buffer_size, dtype='f')
        else:
            raise PulsevizException('buffer_size is too small: {0} < {1}'.format(buffer_size, sample_size))

    @property
    def lock(self):
        return self._samples_lock

    @property
    def sample_size(self):
        return len(self._samples)

    @property
    def samples(self):
        return self._samples

    @property
    def buffer(self):
        if self._buffer is None:
            raise PulsevizException('buffer_size has not been set.')

        return self._buffer

    @property
    def buffer_size(self):
        if self._buffer is None:
            raise PulsevizException('buffer_size has not been set.')

        return len(self._buffer)

    def _sample(self):
        samples = self._pulseaudio_client.read(size=self.sample_size)
        with self.lock:
            self._samples[:] = samples

            if self._buffer is not None:
                n = self.buffer_size - self.sample_size
                self._buffer[0:n] = self._buffer[self.sample_size:]
                self._buffer[n:] = samples
