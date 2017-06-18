import numpy
import threading
from .sampler import Sampler


class SpectrumAnalayzer(Sampler):
    def __init__(self, **kwargs):
        super(SpectrumAnalayzer, self).__init__(**kwargs)
        self.fft_left_side = numpy.zeros(int(self.sample_size / 2), dtype='f')
        self.fftfreq_left_side = numpy.zeros(int(self.sample_size / 2), dtype='f')
        self.fft_left_side_lock = threading.Lock()

    def sample(self):
        super(SpectrumAnalayzer, self).sample()
        self.fft()

    def fft(self):
        fft = numpy.fft.rfft(self.samples)
        fftfreq = numpy.fft.rfftfreq(self.sample_size, 1.0 / self._pulseaudio_client.sample_frequency)
        with self.fft_left_side_lock:
            self.fft_left_side = numpy.abs(fft)
            self.fftfreq_left_side = fftfreq
