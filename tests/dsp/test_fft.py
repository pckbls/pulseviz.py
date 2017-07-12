import time
import pytest
from pulseviz.dsp.fft import FFT


@pytest.mark.parametrize('window_function', [None, 'hanning'])
@pytest.mark.parametrize('output', ['fft', 'psd'])
def test_analyze(fixture_fake_simple_client, window_function, output):
    analyzer = FFT(sample_size=2048,
                   window_function=window_function,
                   output=output,
                   source_name='foobar',
                   stream_name='pulseviz-tests')

    with analyzer:
        time.sleep(1.0)

    assert analyzer.exit_success


def test_frequencies_and_psd_length():
    analyzer = FFT(sample_size=2048,
                   source_name='foobar',
                   stream_name='pulseviz-tests')

    assert analyzer.frequencies[0] == 0.0
    assert len(analyzer.frequencies) == len(analyzer.values)


@pytest.mark.parametrize('window_function', [None, 'hanning'])
@pytest.mark.parametrize('output', ['fft', 'psd'])
def test_benchmark(fixture_fake_simple_client, benchmark, window_function, output):
    analyzer = FFT(sample_size=2048,
                   window_function=window_function,
                   output=output,
                   source_name='foobar',
                   stream_name='pulseviz-tests')

    def benchmark_func():
        for _ in range(0, 1000):
            analyzer._sample()

    analyzer._pulseaudio_client.connect()
    benchmark(benchmark_func)
    analyzer._pulseaudio_client.disconnect()

