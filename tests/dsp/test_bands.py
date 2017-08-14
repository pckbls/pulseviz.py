import pytest
import numpy.testing
from pulseviz.dsp import bands
from pulseviz import PulsevizException


@pytest.fixture
def fixture_octave_bands(fixture_fake_simple_client, request):
    return {
        'source_name': 'foobar',
        'stream_name': 'pulseviz-tests',
        'sample_size': 2048,
        'window_size': 2048,
        'band_frequencies': bands.calculate_octave_bands(fraction=1)
    }


def test_octave_bands_center_frequencies():
    # Reference values taken from: http://www.engineeringtoolbox.com/octave-bands-frequency-limits-d_1602.html
    reference_center_frequencies = [16.0, 31.5, 63.0, 125.0, 250.0, 500.0, 1000.0, 2000.0, 4000.0, 8000.0, 16000.0]

    frequencies = bands.calculate_octave_bands(fraction=1)
    center_frequencies = [(lower + upper) / 2 for lower, upper in frequencies]
    numpy.testing.assert_allclose(reference_center_frequencies, center_frequencies, 1)


@pytest.mark.parametrize('sample_size,fraction', [(2048, 1), (8192, 2), (8192, 3)])
@pytest.mark.parametrize('weighting', ['A', 'C', 'Z'])
def test_analyze(fixture_octave_bands, sample_size, fraction, weighting):
    fixture_octave_bands['sample_size'] = sample_size
    fixture_octave_bands['band_frequencies'] = bands.calculate_octave_bands(fraction)
    fixture_octave_bands['weighting'] = weighting
    analyzer = bands.Bands(**fixture_octave_bands)
    with analyzer:
        pass
    assert analyzer.exit_success


@pytest.mark.skip(reason='No idea how to fix this yet.')
@pytest.mark.parametrize('fraction', [1, 2, 3, 9])
def test_octave_bands_frequencies(fixture_octave_bands, fraction):
    fixture_octave_bands['band_frequencies'] = bands.calculate_octave_bands(fraction)
    analyzer = bands.Bands(**fixture_octave_bands)

    for a, b in zip(analyzer.frequencies, analyzer.frequencies[1:]):
        if b[0] < a[2]:
            raise Exception('Frequencies overlap: {0} {1} (difference: {2})'.format(b[0], a[2], b[0] - a[2]))


@pytest.mark.parametrize('fraction,sample_size', [(1, 512), (2, 2048), (3, 4096)])
def test_octave_bands_fft_resolution_too_small(fixture_octave_bands, sample_size, fraction):
    fixture_octave_bands['band_frequencies'] = bands.calculate_octave_bands(fraction)
    fixture_octave_bands['sample_size'] = sample_size
    with pytest.raises(PulsevizException):
        bands.Bands(**fixture_octave_bands)


@pytest.mark.skip(reason='No idea how to fix this yet.')
@pytest.mark.parametrize('fraction,sample_size', [(1, 2048), (2, 6144), (3, 8192)])
def test_octave_bands_indices(fixture_octave_bands, fraction, sample_size):
    fixture_octave_bands['band_frequencies'] = bands.calculate_octave_bands(fraction)
    fixture_octave_bands['sample_size'] = sample_size
    analyzer = bands.Bands(**fixture_octave_bands)

    a, b = 0, 0
    for lower, upper in zip(analyzer._indices_lower, analyzer._indices_upper):
        if lower == upper:
            raise Exception('Indices equal, resulting in empty slice: [{0}, {1}]'.format(lower, upper))

        if lower <= a or upper <= b:
            raise Exception('Indices overlap: [{0}, {1}] / [{2}, {3}]'.format(a, b, lower, upper))
        a, b = lower, upper


@pytest.mark.parametrize('fraction', [1, 3, 6, 9])
@pytest.mark.parametrize('weighting', ['A', 'C', 'Z'])
def test_benchmark(fixture_octave_bands, benchmark, fraction, weighting):
    fixture_octave_bands['fraction'] = 1
    fixture_octave_bands['weighting'] = 'Z'
    analyzer = bands.Bands(**fixture_octave_bands)

    def benchmark_func():
        for _ in range(0, 1000):
            analyzer._sample()

    analyzer._pulseaudio_client.connect()
    benchmark(benchmark_func)
    analyzer._pulseaudio_client.disconnect()
