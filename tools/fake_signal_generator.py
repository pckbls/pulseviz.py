#!/usr/bin/env python3

#
# A small utility that loads a null sink and plays a fake signal coming from a signal generator to the sink.
#

import sys
import os
import signal
import subprocess
import threading
import numpy

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
from pulseviz.pulseaudio.simple_client import SimplePlaybackClient  # noqa


def sine_generator(sample_frequency):
    t = 0.0
    while True:
        yield numpy.sin(t)
        t += 0.05


def random_generator():
    random.seed(1337)
    while True:
        yield random.random() * 2.0 - 1.0


class SignalGeneratorThread(threading.Thread):
    def __init__(self, generator, **kwargs):
        super().__init__(**kwargs)
        self._sink_name = 'null'
        self._sample_frequency = 44100
        self._sample_size = 2048
        self._pa_client = SimplePlaybackClient(sink=self._sink_name,
                                               sample_frequency=self._sample_frequency)
        self._signal_generator = generator(sample_frequency=self._sample_frequency)
        self._stop_event = threading.Event()

    def load_module_null_sink(self):
        process = subprocess.run([
            'pacmd',
            'load-module',
            'module-null-sink',
            'sink_name="{0}"'.format(self._sink_name)
        ])
        assert process.returncode == 0

    def unload_module_null_sink(self):
        subprocess.run(['pacmd', 'unload-module', 'module-null-sink'])

    def read_samples_from_signal_generator(self, n):
        return [next(self._signal_generator) for _ in range(n)]

    def stop(self):
        self._stop_event.set()

    def run(self):
        self.unload_module_null_sink()
        self.load_module_null_sink()

        with self._pa_client:
            while not self._stop_event.is_set():
                samples = self.read_samples_from_signal_generator(self._sample_size)

                # Convert the samples for SampleFormat.PA_SAMPLE_U8
                # TODO: Use self._pa_client.write_samples() instead.
                quantized_samples = [int((x + 1.0) * 128.0) for x in samples]

                self._pa_client.write(quantized_samples)

            self._pa_client.drain()

        self.unload_module_null_sink()


if __name__ == '__main__':
    sg = SignalGeneratorThread(generator=sine_generator)
    sg.start()
    signal.signal(signal.SIGINT, lambda signal, frame: sg.stop())
    sg.join()
