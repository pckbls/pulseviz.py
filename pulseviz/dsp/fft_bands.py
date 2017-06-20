import numpy
import numpy as np
import math
import threading
from .fft import FFTAnalyzer


class FFTBandsAnalayzer(FFTAnalyzer):
    def __init__(self, **kwargs):
        super(FFTBandsAnalayzer, self).__init__(**kwargs)
        self.fft_bands_lock = threading.Lock()
    
    def set_frequency_bands(self, bands):
        self.fft_bands_frequencies = bands
        self.fft_bands = np.zeros(len(self.fft_bands_frequencies))

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
