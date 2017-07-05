import threading
import numpy
from .sampler import Sampler


class FFTAnalyzer(Sampler):
    """
    Applies the Real Discrete Fourier Transformation to the sampled signal and optionally multiplies it with a
    window function first.
    """

    def __init__(self, window_function=None, **kwargs):
        super(FFTAnalyzer, self).__init__(**kwargs)

        self.fft_lock = threading.Lock()
        self.fft_frequencies = numpy.fft.rfftfreq(self.sample_size,
                                                  1.0 / self._pulseaudio_client.sample_frequency)
        self.fft = numpy.zeros(int(self.sample_size / 2), dtype='f')

        if window_function is None:
            self._window_function = numpy.ones(self.sample_size)
        elif window_function == 'hanning':
            self._window_function = numpy.hanning(self.sample_size)
        else:
            raise Exception('Unknown window function: {0}'.format(window_function))

    def _sample(self):
        super(FFTAnalyzer, self)._sample()

        fft = numpy.abs(numpy.fft.rfft(self._window_function * self.samples))
        with self.fft_lock:
            self.fft = fft
