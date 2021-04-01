import numpy
from .. import PulsevizException
from .sampler import Sampler
from ..pulseaudio.simple_client import SampleFormat


def calculate_frequency_weighting(frequency, weighting):
    """
    Calculates the weighting in [dB] for a given frequency.
    """

    if weighting == 'A':
        a = numpy.power(12194.0, 2) * numpy.power(frequency, 4)
        b = (numpy.power(frequency, 2) + numpy.power(20.6, 2))
        c = (numpy.power(frequency, 2) + numpy.power(107.7, 2))
        d = (numpy.power(frequency, 2) + numpy.power(737.9, 2))
        e = (numpy.power(frequency, 2) + numpy.power(12194.0, 2))
        R_A = a / (b * numpy.sqrt(c * d) * e)
        A = 20 * numpy.log10(R_A) + 2.0
        return A
    elif weighting == 'C':
        a = numpy.power(12194.0, 2) * numpy.power(frequency, 2)
        b = (numpy.power(frequency, 2) + numpy.power(20.6, 2))
        c = (numpy.power(frequency, 2) + numpy.power(12194.0, 2))
        R_C = (a / (b * c))
        C = 20 * numpy.log10(R_C) + 0.06
        return C
    elif weighting == 'Z':
        return 1.0
    else:
        raise Exception('Unknown weighting type: {0}'.format(weighting))


class FFT(Sampler):
    """
    Applies the Real Discrete Fourier Transformation to the sampled signal and optionally multiplies it with a
    window function first.
    """

    def __init__(self, sample_size, window_size,
                 output='fft', scaling='lin',
                 window_function='rectangle', window_overlap=0.0,
                 weighting='Z', **kwargs):
        kwargs['buffer_size'] = sample_size  # TODO: Explain
        kwargs['sample_size'] = int(numpy.floor(window_size * (1.0 - window_overlap)))
        super().__init__(**kwargs)

        self._window_size = window_size

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

        if window_function == 'rectangle':
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

        self._fft_weights = numpy.array([calculate_frequency_weighting(f, weighting)
                                         for f in self._fft_frequencies])

    @property
    def frequencies(self):
        return self._fft_frequencies

    @property
    def values(self):
        return self._fft_values

    def _sample(self):
        super()._sample()

        self._fft_values[:] = numpy.abs(numpy.fft.rfft(self._window_function * self.buffer))

        if self._output == 'fft':
            pass
        elif self._output == 'psd':
            # Reminder for future-self:
            # Our Input signal is clamped between -1.0 and +1.0 yet if we convert the values above ^ into dB
            # we get values way beyond 0dB which makes no sense. Turns out we have to normalize the resulting
            # vector.
            # Thank you my hero: https://dsp.stackexchange.com/a/32080
            # TODO: This can be pre-calculated!
            self._fft_values[:] = numpy.power(self._fft_values * 2.0, 2) \
                / numpy.power(self._window_function_sum * self._reference_value, 2)
        else:
            raise PulsevizException('This should not happen.')

        if self._scaling == 'lin':
            pass
        elif self._scaling == 'log':
            numpy.seterr(divide='ignore')
            self._fft_values[:] = 10.0 * numpy.log10(self._fft_values)
            numpy.seterr(all='raise')  # TODO: Use result of numpy.geterr instead?
        else:
            raise PulsevizException('This should not happen.')

        if self._scaling == 'log':
            self._fft_values[:] += self._fft_weights
        else:
            self._fft_values[:] *= numpy.power(10, self._fft_weights / 20)  # TODO: Test this.
