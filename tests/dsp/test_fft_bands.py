from pulseviz.dsp.fft_bands import FFTBandsAnalayzer
from .. import signal_generators


def test_fft_bands_benchmark(fake_simple_record_client, benchmark):
    client = fake_simple_record_client
    client.attach_signal_generator(signal_generators.random_generator)

    analyzer = FFTBandsAnalayzer(sample_size=44100,
                                 pulseaudio_client=fake_simple_record_client)
    analyzer.generate_octave_bands(fraction=3)

    def benchmark_func():
        for _ in range(0, 10):
            analyzer._sample()

    benchmark(benchmark_func)
