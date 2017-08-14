import pytest
from pulseviz import PulsevizException
from pulseviz.dsp.sampler import Sampler


@pytest.fixture
def fixture_sampler(fixture_fake_simple_client):
    return {
        'source_name': 'foobar',
        'stream_name': 'pulseviz-tests'
    }


@pytest.mark.parametrize('sample_frequency', [44100, 48000, 96000])
@pytest.mark.parametrize('sample_size', [2**8])
@pytest.mark.parametrize('buffer_size', [2**8, 2**9, 2**10, 2**11, 2**12, 2**13, 2**14, 2**15, 2**16])
def test_analyze(fixture_sampler, sample_frequency, sample_size, buffer_size):
    fixture_sampler['sample_frequency'] = sample_frequency
    fixture_sampler['sample_size'] = sample_size
    fixture_sampler['buffer_size'] = buffer_size

    analyzer = Sampler(**fixture_sampler)
    with analyzer:
        pass
    assert analyzer.exit_success


def test_buffer_size(fixture_sampler):
    analyzer = Sampler(sample_size=1024, buffer_size=None, **fixture_sampler)
    assert analyzer.buffer_size == analyzer.sample_size

    with pytest.raises(PulsevizException):
        analyzer = Sampler(sample_size=1024, buffer_size=1023, **fixture_sampler)

    analyzer = Sampler(sample_size=1024, buffer_size=1025, **fixture_sampler)
    assert analyzer.sample_size == 1024
    assert analyzer.buffer_size == 1025


@pytest.mark.parametrize('sample_frequency', [44100])
@pytest.mark.parametrize('sample_size', [2**8])
@pytest.mark.parametrize('buffer_size', [None, 2**8, 2**9, 2**10, 2**11, 2**12, 2**13, 2**14, 2**15, 2**16])
def test_benchmark(fixture_sampler, benchmark, sample_frequency, sample_size, buffer_size):
    fixture_sampler['sample_frequency'] = sample_frequency
    fixture_sampler['sample_size'] = sample_size
    fixture_sampler['buffer_size'] = buffer_size

    analyzer = Sampler(**fixture_sampler)

    def benchmark_func():
        for _ in range(0, 1000):
            analyzer._sample()

    analyzer._pulseaudio_client.connect()
    benchmark(benchmark_func)
    analyzer._pulseaudio_client.disconnect()
