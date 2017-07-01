import threading


class PulseAudioSignalAnalayzer(threading.Thread):
    def __init__(self, pulseaudio_client, **kwargs):
        super().__init__(**kwargs)

        self._pulseaudio_client = pulseaudio_client
        self._stop_event = threading.Event()

    def run(self):
        with self._pulseaudio_client:
            while not self._stop_event.is_set():
                self._sample()

    def stop(self):
        self._stop_event.set()

    def _sample(self):
        # TODO: Read and save latency
        pass
