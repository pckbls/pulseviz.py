import threading
import time
import numpy


class Sampler(threading.Thread):
    def __init__(self, pulseaudio_client, sample_size, **kwargs):
        super(Sampler, self).__init__(**kwargs)

        self._pulseaudio_client = pulseaudio_client
        self._stop_event = threading.Event()

        self.sample_size = sample_size
        self.samples_lock = threading.Lock()
        self.samples = numpy.zeros(self.sample_size, dtype='f')

    def run(self):
        with self._pulseaudio_client:
            while not self._stop_event.is_set():
                self.sample()

    def stop(self):
        self._stop_event.set()

    def sample(self):
        samples = self._pulseaudio_client.read_samples(size=self.sample_size)
        with self.samples_lock:
            self.samples = numpy.array(samples, dtype='f')