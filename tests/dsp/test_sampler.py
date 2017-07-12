import time
import pytest
from pulseviz.dsp.sampler import Sampler


@pytest.mark.parametrize('sample_frequency', [44100, 48000, 96000])
def test_analyze(fixture_fake_simple_client, sample_frequency):
    analyzer = Sampler(sample_frequency=sample_frequency,
                       sample_size=2048,
                       source_name='foobar',
                       stream_name='pulseviz-tests')

    with analyzer:
        time.sleep(1.0)

    assert analyzer.exit_success


def test_benchmark(fixture_fake_simple_client, benchmark):
    analyzer = Sampler(sample_frequency=44100,
                       sample_size=2048,
                       source_name='foobar',
                       stream_name='pulseviz-tests')

    def benchmark_func():
        for _ in range(0, 1000):
            analyzer._sample()

    analyzer._pulseaudio_client.connect()
    benchmark(benchmark_func)
    analyzer._pulseaudio_client.disconnect()
