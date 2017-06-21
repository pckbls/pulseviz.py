import threading
import numpy
from .sampler import Sampler


class FFTAnalyzer(Sampler):
    def __init__(self, **kwargs):
        super(FFTAnalyzer, self).__init__(**kwargs)

        self.fft_lock = threading.Lock()
        self.fft = numpy.zeros(int(self.sample_size / 2), dtype='f')
        self.fft_frequencies = numpy.zeros(int(self.sample_size / 2), dtype='f')

    def _sample(self):
        super(FFTAnalyzer, self)._sample()
        with self.fft_lock:
            self._calculate_fft()

    def _calculate_fft(self):
        self.fft = numpy.abs(numpy.fft.rfft(self.samples))
        self.fft_frequencies = numpy.fft.rfftfreq(self.sample_size,
                                                  1.0 / self._pulseaudio_client.sample_frequency)
