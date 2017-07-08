import threading
import random
import numpy
from pulseviz.pulseaudio.simple_client import SimplePlaybackClient, SampleFormat


def random_generator(sample_frequency):
    random.seed(1337)
    while True:
        yield random.random() * 2.0 - 1.0


def sine_generator(sample_frequency):
    t = 0.0
    while True:
        yield numpy.sin(t)
        t += 0.05


def null_generator(sample_frequency):
    while True:
        yield 0.0


class SignalGenerator(threading.Thread):
    """
    The SignalGenerator can be used to generate audio signals of different shapes.
    """

    def __init__(self, sink_name, sample_frequency=44100, sample_size=2048, **kwargs):
        super().__init__(**kwargs)
        self._sink_name = sink_name
        self._sample_frequency = sample_frequency
        self._sample_size = sample_size
        self._pa_client = SimplePlaybackClient(sink=self._sink_name,
                                               sample_frequency=self._sample_frequency,
                                               sample_format=SampleFormat.PA_SAMPLE_U8,  # TODO
                                               channels=1)
        self._stop_event = threading.Event()

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        self.join()

    def attach_generator(self, generator_name='null', **kwargs):
        """Configures and attaches a signal generator."""

        if generator_name == 'null':
            generator_type = null_generator
        elif generator_name == 'sine':
            generator_type = sine_generator
        elif generator_name == 'random':
            generator_type = random_generator
        else:
            raise Exception('Unknown generator name "{0}"'.format(generator_name))

        self._signal_generator = generator_type(sample_frequency=self._sample_frequency, **kwargs)

        return self

    def stop(self):
        self._stop_event.set()

    def _read_samples_from_signal_generator(self, n):
        return [next(self._signal_generator) for _ in range(n)]

    def run(self):
        with self._pa_client:
            while not self._stop_event.is_set():
                samples = self._read_samples_from_signal_generator(self._sample_size)

                # TODO: Use FLOAT32LE instead
                quantized_samples = [int((x + 1.0) * 128.0) for x in samples]

                self._pa_client.write(quantized_samples)

            self._pa_client.flush()
