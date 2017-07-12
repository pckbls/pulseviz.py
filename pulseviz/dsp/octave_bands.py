import threading
import numpy
from .fft import FFT


class OctaveBands(FFT):
    """
    Divides the results of the FFT into (second, third, ...) octave bands.
    For each band the results of the FFT are averaged and saved.
    Optionally a band weighting function can be applied.
    """

    def __init__(self, weighting='Z', fraction=1, **kwargs):
        kwargs['output'] = 'fft'
        super().__init__(**kwargs)

        self._bands_lock = threading.Lock()
        self._bands_frequencies = self._calculate_octave_bands_frequencies(fraction=fraction)
        self._bands_values = -numpy.inf * numpy.ones(len(self._bands_frequencies))
        self._bands_weights = self._calculate_bands_weighting(weighting)

        self._indices_lower = [0] * len(self._bands_frequencies)
        self._indices_upper = [0] * len(self._bands_frequencies)
        for i, (lower, _, upper) in enumerate(self._bands_frequencies):
            k = self.sample_size / self._pulseaudio_client.sample_frequency
            self._indices_lower[i] = int(numpy.ceil(lower * k))
            self._indices_upper[i] = int(numpy.ceil(upper * k))

    @property
    def lock(self):
        return self._bands_lock

    @property
    def n(self):
        """Returns the number of bands."""

        return len(self._bands_frequencies)

    @property
    def frequencies(self):
        return self._bands_frequencies

    @property
    def values(self):
        return self._bands_values

    def _calculate_octave_bands_frequencies(self, fraction=1):
        bands_numbers = numpy.linspace(-6, 4, 11 * fraction)
        center_frequencies = numpy.power(10.0, 3) * numpy.power(2.0, bands_numbers)
        bands_frequencies = []

        for center in center_frequencies:
            fd = numpy.power(2, 1 / 2)
            lower = center / fd
            upper = center * fd
            bands_frequencies.append((lower, center, upper))

        return bands_frequencies

    def _calculate_bands_weighting(self, weighting):
        return [self._calculate_weighting_for_frequency(f, weighting) for _, f, _ in self._bands_frequencies]

    def _calculate_weighting_for_frequency(self, frequency, weighting):
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

    def _sample(self):
        super()._sample()

        with self.lock:
            # TODO: We can probably eliminate all for loops and perform a matrix multiplication instead which would
            # be really really fast!
            for i, _ in enumerate(self._bands_frequencies):
                m = self._indices_lower[i]
                n = self._indices_upper[i]

                # TODO: Is the way we calculate the octave band magnitutes really correct? :/
                # self.bands_values[i] = numpy.sum(self.fft[m:n]) / (upper - lower)
                self._bands_values[i] = numpy.average(super().values[m:n])

            if 0 in self._bands_values:
                self._bands_values[:] = -numpy.inf * numpy.ones(len(self._bands_frequencies))
            else:
                self._bands_values[:] = 20 * numpy.log10(self._bands_values)

            for i, _ in enumerate(self._bands_frequencies):
                self._bands_values[i] += self._bands_weights[i]
