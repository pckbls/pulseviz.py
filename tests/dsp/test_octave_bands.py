import pytest
import numpy.testing
from pulseviz.dsp.octave_bands import OctaveBands
from pulseviz import PulsevizException


@pytest.fixture
def fixture_octave_bands(fixture_fake_simple_client, request):
    return {
        'source_name': 'foobar',
        'stream_name': 'pulseviz-tests',
        'sample_size': 2048,
        'buffer_size': 2048
    }


@pytest.mark.parametrize('buffer_size,fraction', [(2048, 1), (8192, 2), (8192, 3)])
@pytest.mark.parametrize('weighting', ['A', 'C', 'Z'])
def test_analyze(fixture_octave_bands, buffer_size, fraction, weighting):
    fixture_octave_bands['buffer_size'] = buffer_size
    fixture_octave_bands['fraction'] = fraction
    fixture_octave_bands['weighting'] = weighting
    analyzer = OctaveBands(**fixture_octave_bands)
    with analyzer:
        pass
    assert analyzer.exit_success


def test_octave_bands_center_frequencies(fixture_octave_bands):
    fixture_octave_bands['fraction'] = 1
    analyzer = OctaveBands(**fixture_octave_bands)

    # Reference values taken from: http://www.engineeringtoolbox.com/octave-bands-frequency-limits-d_1602.html
    reference_center_frequencies = [16.0, 31.5, 63.0, 125.0, 250.0, 500.0, 1000.0, 2000.0, 4000.0, 8000.0, 16000.0]
    center_frequencies = [center for _, center, _ in analyzer.frequencies]
    numpy.testing.assert_allclose(reference_center_frequencies, center_frequencies, 1)


@pytest.mark.skip(reason='No idea how to fix this yet.')
@pytest.mark.parametrize('fraction', [1, 2, 3, 9])
def test_octave_bands_frequencies(fixture_octave_bands, fraction):
    fixture_octave_bands['fraction'] = fraction
    analyzer = OctaveBands(**fixture_octave_bands)

    for a, b in zip(analyzer.frequencies, analyzer.frequencies[1:]):
        if b[0] < a[2]:
            raise Exception('Frequencies overlap: {0} {1} (difference: {2})'.format(b[0], a[2], b[0] - a[2]))


@pytest.mark.parametrize('fraction,buffer_size', [(1, 512), (2, 2048), (3, 4096)])
def test_octave_bands_fft_resolution_too_small(fixture_octave_bands, buffer_size, fraction):
    fixture_octave_bands['fraction'] = fraction
    fixture_octave_bands['buffer_size'] = buffer_size
    with pytest.raises(PulsevizException):
        OctaveBands(**fixture_octave_bands)


@pytest.mark.skip(reason='No idea how to fix this yet.')
@pytest.mark.parametrize('fraction,buffer_size', [(1, 2048), (2, 6144), (3, 8192)])
def test_octave_bands_indices(fixture_octave_bands, fraction, buffer_size):
    fixture_octave_bands['fraction'] = fraction
    fixture_octave_bands['buffer_size'] = buffer_size
    analyzer = OctaveBands(**fixture_octave_bands)

    a, b = 0, 0
    for lower, upper in zip(analyzer._indices_lower, analyzer._indices_upper):
        if lower == upper:
            raise Exception('Indices equal, resulting in empty slice: [{0}, {1}]'.format(lower, upper))

        if lower <= a or upper <= b:
            raise Exception('Indices overlap: [{0}, {1}] / [{2}, {3}]'.format(a, b, lower, upper))
        a, b = lower, upper


def test_A_weighting(fixture_octave_bands):
    fixture_octave_bands['fraction'] = 1
    fixture_octave_bands['weighting'] = 'A'
    analyzer = OctaveBands(**fixture_octave_bands)

    # Reference values taken from: https://www.vernier.com/til/3500/
    frequencies = [31.5, 63.0, 125.0, 250.0, 500.0, 1000.0, 2000.0, 4000.0, 8000.0]
    reference_A_weightings = [-39.4, -26.2, -16.1, -8.6, -3.2, 0.0, 1.2, 1.0, -1.1]
    A_weightings = [analyzer._calculate_weighting_for_frequency(f, 'A') for f in frequencies]

    numpy.testing.assert_allclose(reference_A_weightings, A_weightings, 1)


@pytest.mark.skip(reason='Not implemented yet.')
def test_C_weighting():
    raise Exception('Not implemented yet.')


def test_Z_weighting(fixture_octave_bands):
    fixture_octave_bands['fraction'] = 1
    fixture_octave_bands['weighting'] = 'Z'
    analyzer = OctaveBands(**fixture_octave_bands)

    assert analyzer._calculate_weighting_for_frequency(0.0, 'Z') == 1.0
    assert analyzer._calculate_weighting_for_frequency(1337.0, 'Z') == 1.0
    assert analyzer._calculate_weighting_for_frequency(20000.0, 'Z') == 1.0


@pytest.mark.parametrize('fraction', [1, 3, 6, 9])
@pytest.mark.parametrize('weighting', ['A', 'C', 'Z'])
def test_benchmark(fixture_octave_bands, benchmark, fraction, weighting):
    fixture_octave_bands['fraction'] = 1
    fixture_octave_bands['weighting'] = 'Z'
    analyzer = OctaveBands(**fixture_octave_bands)

    def benchmark_func():
        for _ in range(0, 1000):
            analyzer._sample()

    analyzer._pulseaudio_client.connect()
    benchmark(benchmark_func)
    analyzer._pulseaudio_client.disconnect()
