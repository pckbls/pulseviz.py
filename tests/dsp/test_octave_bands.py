import time
import pytest
import numpy.testing
from pulseviz.dsp.octave_bands import OctaveBands


@pytest.mark.parametrize('fraction', [1, 2, 3])
@pytest.mark.parametrize('weighting', ['A', 'C', 'Z'])
def test_analyze(fixture_fake_simple_client, fraction, weighting):
    analyzer = OctaveBands(sample_size=2048,
                           fraction=fraction,
                           weighting=weighting,
                           source_name='foobar',
                           stream_name='pulseviz-tests')

    with analyzer:
        time.sleep(1.0)

    assert analyzer.exit_success


def test_octave_bands_center_frequencies():
    analyzer = OctaveBands(sample_size=44100,
                           fraction=1,
                           source_name='whatever')

    # Reference values taken from: http://www.engineeringtoolbox.com/octave-bands-frequency-limits-d_1602.html
    reference_center_frequencies = [16.0, 31.5, 63.0, 125.0, 250.0, 500.0, 1000.0, 2000.0, 4000.0, 8000.0, 16000.0]
    center_frequencies = [center for _, center, _ in analyzer.frequencies]
    numpy.testing.assert_allclose(reference_center_frequencies, center_frequencies, 1)


def test_frequency_bins_do_not_overlap():
    analyzer = OctaveBands(sample_size=2048,
                           source_name='foobar',
                           stream_name='pulseviz-tests')

    a, b = 0, 0
    for lower, upper in zip(analyzer._indices_lower, analyzer._indices_upper):
        if lower <= a or upper <= b:
            raise Exception('Frequency bins overlap!')
        a, b = lower, upper


def test_A_weighting():
    analyzer = OctaveBands(sample_size=2048,
                           fraction=1,
                           weighting='A',
                           source_name='whatever')

    # Reference values taken from: https://www.vernier.com/til/3500/
    frequencies = [31.5, 63.0, 125.0, 250.0, 500.0, 1000.0, 2000.0, 4000.0, 8000.0]
    reference_A_weightings = [-39.4, -26.2, -16.1, -8.6, -3.2, 0.0, 1.2, 1.0, -1.1]
    A_weightings = [analyzer._calculate_weighting_for_frequency(f, 'A') for f in frequencies]

    numpy.testing.assert_allclose(reference_A_weightings, A_weightings, 1)


@pytest.mark.skip(reason='Not implemented yet.')
def test_C_weighting():
    raise Exception('Not implemented yet.')


def test_Z_weighting():
    analyzer = OctaveBands(sample_size=2048,
                           fraction=1,
                           weighting='Z',
                           source_name='pulseviz-tests')

    assert analyzer._calculate_weighting_for_frequency(0.0, 'Z') == 1.0
    assert analyzer._calculate_weighting_for_frequency(1337.0, 'Z') == 1.0
    assert analyzer._calculate_weighting_for_frequency(20000.0, 'Z') == 1.0


@pytest.mark.parametrize('fraction', [1, 3, 6, 9])
@pytest.mark.parametrize('weighting', ['A', 'C', 'Z'])
def test_benchmark(fixture_fake_simple_client, benchmark, fraction, weighting):
    analyzer = OctaveBands(sample_size=2048,
                           fraction=fraction,
                           weighting=weighting,
                           source_name='foobar',
                           stream_name='pulseviz-tests')

    def benchmark_func():
        for _ in range(0, 1000):
            analyzer._sample()

    analyzer._pulseaudio_client.connect()
    benchmark(benchmark_func)
    analyzer._pulseaudio_client.disconnect()
