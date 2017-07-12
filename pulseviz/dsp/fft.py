import threading
import numpy
from .sampler import Sampler
from ..pulseaudio.simple_client import SampleFormat


class FFT(Sampler):
    """
    Applies the Real Discrete Fourier Transformation to the sampled signal and optionally multiplies it with a
    window function first.
    """

    def __init__(self, window_function=None, output='fft', **kwargs):
        super().__init__(**kwargs)

        self._fft_lock = threading.Lock()
        self._fft_frequencies = numpy.fft.rfftfreq(self.sample_size,
                                                   1.0 / self._pulseaudio_client.sample_frequency)
        self._fft_values = numpy.zeros(int(self.sample_size / 2) + 1, dtype='f')

        if output not in ['fft', 'psd']:
            raise Exception('Unknown output type: {0}'.format(output))

        self._output = output

        if window_function is None:
            self._window_function = numpy.ones(self.sample_size)
        elif window_function == 'hanning':
            self._window_function = numpy.hanning(self.sample_size)
        else:
            raise Exception('Unknown window function: {0}'.format(window_function))

        self._window_function_sum = numpy.sum(self._window_function)

        if self._pulseaudio_client.sample_format == SampleFormat.PA_SAMPLE_FLOAT32LE:
            self._reference_value = 1.0
        else:
            raise Exception('Chosen sample format is not supported.')

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
            self._fft_values[:] = numpy.abs(numpy.fft.rfft(self._window_function * self.samples))

            # Reminder for future-self:
            # Our Input signal is clamped between -1.0 and +1.0 yet if we convert the values above ^ into dB
            # we get values way beyond 0dB which makes no sense. Turns out we have to normalize the resulting vector.
            # Thanks you my hero: https://dsp.stackexchange.com/a/32080
            self._fft_values[:] = self._fft_values * 2.0 / self._window_function_sum

            if self._output == 'fft':
                pass
            elif self._output == 'psd':
                if 0 in self._fft_values:
                    self._fft_values[:] = -numpy.inf * numpy.ones(len(self._fft_frequencies))
                else:
                    self._fft_values[:] = 20 * numpy.log10(self._fft_values / self._reference_value)  # in dbFS
            else:
                raise Exception('This should not happen.')
