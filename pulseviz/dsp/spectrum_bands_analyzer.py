import numpy
import numpy as np
import math
import threading
from .spectrum_analyzer import SpectrumAnalayzer


class SpectrumBandsAnalayzer(SpectrumAnalayzer):
    def __init__(self, **kwargs):
        super(SpectrumBandsAnalayzer, self).__init__(**kwargs)

        self.bands_lock = threading.Lock()
        self.frequency_bins = [
            (0, 50),
            (50, 100),
            (100, 200),
            (200, 400),
            (400, 800),
            (800, 1600),
            (1600, 3200),
            (3200, 6400),
            (6400, 12800),
            (12800, 22050)
        ]
        self.frequency_bins_values = np.zeros(len(self.frequency_bins))

    def sample(self):
        super(SpectrumBandsAnalayzer, self).sample()
        with self.bands_lock:
            self.average_fft()
    
    def average_fft(self):
        self.frequency_bins_values = []
        for lower, upper in self.frequency_bins:
            blubb = []
            for freq, value in zip(self.fftfreq_left_side, self.fft_left_side):
                if lower <= freq <= upper:
                    blubb.append(value)
            self.frequency_bins_values.append(sum(blubb) / (upper - lower))
