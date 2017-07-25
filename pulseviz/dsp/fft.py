import threading
import numpy
from .. import PulsevizException
from .sampler import Sampler
from ..pulseaudio.simple_client import SampleFormat


class FFT(Sampler):
    """
    Applies the Real Discrete Fourier Transformation to the sampled signal and optionally multiplies it with a
    window function first.
    """

    def __init__(self, output='fft', scaling='lin', window_function='rectangle', **kwargs):
        super().__init__(**kwargs)

        self._fft_lock = threading.Lock()
        self._fft_frequencies = numpy.fft.rfftfreq(self.buffer_size,
                                                   1.0 / self._pulseaudio_client.sample_frequency)
        self._fft_values = numpy.zeros(int(self.buffer_size / 2) + 1, dtype='f')

        if output in ['fft', 'psd']:
            self._output = output
        else:
            raise PulsevizException('Unknown output type: {0}'.format(output))

        if scaling in ['lin', 'log']:
            self._scaling = scaling
        else:
            raise PulsevizException('Unknown scaling type: {0}'.format(scaling))

        if window_function is 'rectangle':
            self._window_function = numpy.ones(self.buffer_size)
        elif window_function == 'hanning':
            self._window_function = numpy.hanning(self.buffer_size)
        else:
            raise PulsevizException('Unknown window function: {0}'.format(window_function))

        self._window_function_sum = numpy.sum(self._window_function)

        if self._pulseaudio_client.sample_format == SampleFormat.PA_SAMPLE_FLOAT32LE:
            self._reference_value = 1.0
        else:
            raise PulsevizException('Chosen sample format is not supported.')

    @property
    def lock(self):
        return self._fft_lock

    @property
    def frequencies(self):
        return self._fft_frequencies

    @property
    def values(self):
        return self._fft_values

    def _sample(self):
        super()._sample()

        with self.lock:
            self._fft_values[:] = numpy.abs(numpy.fft.rfft(self._window_function * self.buffer))

            if self._output == 'fft':
                pass
            elif self._output == 'psd':
                # Reminder for future-self:
                # Our Input signal is clamped between -1.0 and +1.0 yet if we convert the values above ^ into dB
                # we get values way beyond 0dB which makes no sense. Turns out we have to normalize the resulting
                # vector.
                # Thank you my hero: https://dsp.stackexchange.com/a/32080
                self._fft_values[:] = numpy.power(self._fft_values * 2.0, 2) \
                    / numpy.power(self._window_function_sum * self._reference_value, 2)
            else:
                raise PulsevizException('This should not happen.')

            if self._scaling == 'lin':
                pass
            elif self._scaling == 'log':
                if 0 in self._fft_values:
                    self._fft_values[:] = -numpy.inf * numpy.ones(len(self._fft_values))
                else:
                    self._fft_values[:] = 10.0 * numpy.log10(self._fft_values)
            else:
                raise PulsevizException('This should not happen.')
