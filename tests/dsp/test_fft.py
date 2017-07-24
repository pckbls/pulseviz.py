import pytest
from pulseviz.dsp.fft import FFT


@pytest.fixture
def fixture_fft(fixture_fake_simple_client, request):
    return {
        'source_name': 'foobar',
        'stream_name': 'pulseviz-tests',
        'sample_size': 1024,
        'buffer_size': 1024
    }


@pytest.mark.parametrize('sample_size', [512])
@pytest.mark.parametrize('buffer_size', [512, 1024])
@pytest.mark.parametrize('window_function', ['rectangle', 'hanning'])
@pytest.mark.parametrize('output', ['fft', 'psd'])
@pytest.mark.parametrize('scaling', ['lin', 'log'])
def test_analyze(fixture_fft, sample_size, buffer_size, window_function, output, scaling):
    fixture_fft['sample_size'] = sample_size
    fixture_fft['buffer_size'] = buffer_size
    fixture_fft['window_function'] = window_function
    fixture_fft['output'] = output
    fixture_fft['scaling'] = scaling
    analyzer = FFT(**fixture_fft)
    with analyzer:
        pass
    assert analyzer.exit_success


def test_frequencies_and_psd_length(fixture_fft):
    analyzer = FFT(**fixture_fft)
    assert analyzer.frequencies[0] == 0.0
    assert len(analyzer.frequencies) == len(analyzer.values)


def test_benchmark(fixture_fft, benchmark):
    analyzer = FFT(**fixture_fft)

    def benchmark_func():
        for _ in range(0, 1000):
            analyzer._sample()

    analyzer._pulseaudio_client.connect()
    benchmark(benchmark_func)
    analyzer._pulseaudio_client.disconnect()
