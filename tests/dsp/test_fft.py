import pytest
import numpy
from pulseviz.dsp import fft


@pytest.fixture
def fixture_fft(fixture_fake_simple_client, request):
    return {
        'source_name': 'foobar',
        'stream_name': 'pulseviz-tests',
        'sample_size': 1024,
        'window_size': 512
    }


@pytest.mark.parametrize('sample_size', [512, 1024])
@pytest.mark.parametrize('window_size', [512])
@pytest.mark.parametrize('window_overlap', [0.0, 0.5])
@pytest.mark.parametrize('window_function', ['rectangle', 'hanning'])
@pytest.mark.parametrize('output', ['fft', 'psd'])
@pytest.mark.parametrize('scaling', ['lin', 'log'])
@pytest.mark.parametrize('weighting', ['A', 'C', 'Z'])
def test_analyze(fixture_fft, sample_size, window_function, window_size, window_overlap, output, scaling, weighting):
    fixture_fft['sample_size'] = sample_size
    fixture_fft['window_size'] = window_size
    fixture_fft['window_function'] = window_function
    fixture_fft['window_overlap'] = window_overlap
    fixture_fft['output'] = output
    fixture_fft['scaling'] = scaling
    analyzer = fft.FFT(**fixture_fft)
    with analyzer:
        pass
    assert analyzer.exit_success


def test_frequencies_and_psd_length(fixture_fft):
    analyzer = fft.FFT(**fixture_fft)
    assert analyzer.frequencies[0] == 0.0
    assert len(analyzer.frequencies) == len(analyzer.values)


def test_benchmark(fixture_fft, benchmark):
    analyzer = fft.FFT(**fixture_fft)

    def benchmark_func():
        for _ in range(0, 1000):
            analyzer._sample()

    analyzer._pulseaudio_client.connect()
    benchmark(benchmark_func)
    analyzer._pulseaudio_client.disconnect()


def test_A_weighting():
    # Reference values taken from: https://www.vernier.com/til/3500/
    frequencies = [31.5, 63.0, 125.0, 250.0, 500.0, 1000.0, 2000.0, 4000.0, 8000.0]
    reference_A_weightings = [-39.4, -26.2, -16.1, -8.6, -3.2, 0.0, 1.2, 1.0, -1.1]
    A_weightings = [fft.calculate_frequency_weighting(f, 'A') for f in frequencies]
    numpy.testing.assert_allclose(reference_A_weightings, A_weightings, 1)


@pytest.mark.skip(reason='Not implemented yet.')
def test_C_weighting():
    raise Exception('Not implemented yet.')


def test_Z_weighting():
    assert fft.calculate_frequency_weighting(0.0, 'Z') == 1.0
    assert fft.calculate_frequency_weighting(1337.0, 'Z') == 1.0
    assert fft.calculate_frequency_weighting(20000.0, 'Z') == 1.0
