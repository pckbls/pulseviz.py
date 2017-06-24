import threading
import numpy
from .fft import FFTAnalyzer


# TODO: Some useful links:
# https://github.com/python-acoustics/python-acoustics/blob/master/acoustics/bands.py
# http://blog.prosig.com/2006/02/17/standard-octave-bands/
# https://en.wikipedia.org/wiki/Octave_band
# http://www.engineeringtoolbox.com/octave-bands-frequency-limits-d_1602.html


class FFTBandsAnalayzer(FFTAnalyzer):
    def __init__(self, **kwargs):
        super(FFTBandsAnalayzer, self).__init__(**kwargs)
        self.fft_bands_lock = threading.Lock()
        self.fft_bands = None
        self.fft_bands_frequencies = None

    def set_frequency_bands(self, bands):
        self.fft_bands_frequencies = bands
        self.fft_bands = numpy.zeros(len(self.fft_bands_frequencies))

    def generate_octave_bands(self, fraction=1):
        bands_numbers = numpy.linspace(-6, 4, 10 * fraction)
        center_frequencies = numpy.power(10.0, 3) * numpy.power(2.0, bands_numbers)
        bands_frequencies = []
        for freq in center_frequencies:
            fd = numpy.power(2, 1 / 2)
            lower = freq / fd
            upper = freq * fd
            bands_frequencies.append((lower, upper))
        self.set_frequency_bands(bands_frequencies)

    def n(self):
        return len(self.fft_bands_frequencies)

    def _sample(self):
        super(FFTBandsAnalayzer, self)._sample()

        with self.fft_bands_lock:
            for i, (lower, upper) in enumerate(self.fft_bands_frequencies):
                k = self.sample_size / self._pulseaudio_client.sample_frequency
                m = int(numpy.ceil(lower * k))
                n = int(numpy.ceil(upper * k))
                self.fft_bands[i] = numpy.sum(self.fft[m:n]) / (upper - lower)

            self.fft_bands = 20 * numpy.log10(self.fft_bands)
