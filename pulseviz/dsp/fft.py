import threading
import numpy
from .sampler import Sampler


class FFTAnalyzer(Sampler):
    def __init__(self, window_function=None, **kwargs):
        super(FFTAnalyzer, self).__init__(**kwargs)

        if window_function is None:
            self._window_function = numpy.ones(self.sample_size)  # TODO: Correct?
        elif window_function == 'hanning':
            self._window_function = numpy.hanning(self.sample_size)
        else:
            raise Exception('Unknown window function: {0}'.format(window_function))

        self.fft_lock = threading.Lock()
        self.fft = numpy.zeros(int(self.sample_size / 2), dtype='f')
        self.fft_frequencies = numpy.zeros(int(self.sample_size / 2), dtype='f')

    def _sample(self):
        super(FFTAnalyzer, self)._sample()
        with self.fft_lock:
            self._calculate_fft()

    def _calculate_fft(self):
        self.fft = numpy.abs(numpy.fft.rfft(self._window_function * self.samples))
        self.fft_frequencies = numpy.fft.rfftfreq(self.sample_size,
                                                  1.0 / self._pulseaudio_client.sample_frequency)
