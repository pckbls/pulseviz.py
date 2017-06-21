import threading
import numpy
from .fft import FFTAnalyzer


class FFTBandsAnalayzer(FFTAnalyzer):
    def __init__(self, **kwargs):
        super(FFTBandsAnalayzer, self).__init__(**kwargs)
        self.fft_bands_lock = threading.Lock()
        self.fft_bands = None
        self.fft_bands_frequencies = None

    def set_frequency_bands(self, bands):
        self.fft_bands_frequencies = bands
        self.fft_bands = numpy.zeros(len(self.fft_bands_frequencies))

    def _sample(self):
        super(FFTBandsAnalayzer, self)._sample()
        with self.fft_bands_lock:
            self._average_fft()

    def _average_fft(self):
        self.fft_bands = []
        for lower, upper in self.fft_bands_frequencies:
            blubb = []
            for freq, value in zip(self.fft_frequencies, self.fft):
                if lower <= freq <= upper:
                    blubb.append(value)
            self.fft_bands.append(sum(blubb) / (upper - lower))
