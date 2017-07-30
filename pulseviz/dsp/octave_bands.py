import threading
import numpy
from .fft import FFT
from .. import PulsevizException


class OctaveBands(FFT):
    """
    Divides the results of the FFT into (second, third, ...) octave bands.
    For each band the results of the FFT are averaged and saved.
    Optionally a band weighting function can be applied.
    """

    def __init__(self, weighting='Z', fraction=1, **kwargs):
        kwargs['output'] = 'psd'
        kwargs['scaling'] = 'log'
        super().__init__(**kwargs)

        self._bands_lock = threading.Lock()
        self._bands_frequencies = self._calculate_octave_bands_frequencies(fraction=fraction)
        self._bands_values = -numpy.inf * numpy.ones(len(self._bands_frequencies))
        self._bands_weights = self._calculate_bands_weighting(weighting)
        self._indices_lower, self._indices_upper = self._calculate_fft_indices()

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

    def _calculate_fft_indices(self):
        indices_lower = [0] * len(self._bands_frequencies)
        indices_upper = [0] * len(self._bands_frequencies)
        for i, (lower, _, upper) in enumerate(self._bands_frequencies):
            k = self.buffer_size / self._pulseaudio_client.sample_frequency
            max_upper_index = len(super().frequencies) - 1
            indices_lower[i] = int(numpy.clip(numpy.ceil(lower * k), 0, max_upper_index))
            indices_upper[i] = int(numpy.clip(numpy.ceil(upper * k), 0, max_upper_index))

            if not 0 <= indices_lower[i] <= max_upper_index or not 0 <= indices_upper[i] <= max_upper_index:
                raise PulsevizException('Calculated indices are not valid. This should not happen.')

        for lower, upper in zip(indices_lower, indices_upper):
            if lower == upper:
                raise PulsevizException('FFT resolution too low for selected fraction. '
                                        'Either increase buffer_size or choose a lower fraction.')

        return indices_lower, indices_upper

    def _calculate_octave_bands_frequencies(self, fraction=1):
        bands_numbers = numpy.linspace(-6, 4, 11 * fraction)
        center_frequencies = numpy.power(10.0, 3) * numpy.power(2.0, bands_numbers)
        bands_frequencies = []

        for center in center_frequencies:
            # Sources:
            # * https://en.wikipedia.org/wiki/Octave_band
            # * http://www.sengpielaudio.com/calculator-octave.htm
            fd = numpy.power(2.0, 1.0 / (2.0 * fraction))
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
            # For each band we have to calculate the average magnitude for all frequencies that
            # are part of that band. For some odd reason numpy.mean() is _VERY_ slow!
            # numpy.cumsum() on the other hand is blazingly fast.
            fft_cumsum = numpy.cumsum(super().values)

            # TODO: We can probably eliminate all for loops and perform a matrix multiplication instead which would
            # be really really fast!
            for i, (lower, _, upper) in enumerate(self._bands_frequencies):
                m = self._indices_lower[i]
                n = self._indices_upper[i]
                if fft_cumsum[n] == -numpy.inf or fft_cumsum[m] == -numpy.inf:
                    self._bands_values[i] = -numpy.inf
                else:
                    self._bands_values[i] = (fft_cumsum[n] - fft_cumsum[m]) / (n - m)

            for i, _ in enumerate(self._bands_frequencies):
                self._bands_values[i] += self._bands_weights[i]
