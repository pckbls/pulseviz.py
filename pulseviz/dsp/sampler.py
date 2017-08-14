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

        self._samples = self._pulseaudio_client.create_buffer(size=sample_size)

        if buffer_size is None:
            buffer_size = sample_size

        if buffer_size >= sample_size:
            self._buffer = numpy.zeros(buffer_size, dtype='f')
        else:
            raise PulsevizException('buffer_size is too small: {0} < {1}'.format(buffer_size, sample_size))

    @property
    def sample_size(self):
        return len(self._samples)

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
        self._pulseaudio_client.read_into_buffer(self._samples)

        if self._buffer is not None:
            n = self.buffer_size - self.sample_size
            self._buffer[0:n] = self._buffer[self.sample_size:]
            self._buffer[n:] = self._samples
