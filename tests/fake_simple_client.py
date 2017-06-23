from pulseviz.pulseaudio.simple_client import SimpleRecordClient


class FakeSimpleRecordClient(SimpleRecordClient):
    def __init__(self, **kwargs):
        super(FakeSimpleRecordClient, self).__init__(**kwargs)
        self._signal_generator = None

    def attach_signal_generator(self, generator):
        self._signal_generator = generator()

    def read_samples(self, size=1024):
        return [next(self._signal_generator) for _ in range(size)]

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
