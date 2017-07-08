import threading
import numpy
from ..pulseaudio.simple_client import SimpleRecordClient, SampleFormat


class PulseAudioSignalAnalayzer(threading.Thread):
    """
    Establishes a connection to a PulseAudio server and allows to interact with it.
    """

    def __init__(self, source_name, stream_name='none', sample_frequency=44100, **kwargs):
        super().__init__(**kwargs)

        self._pulseaudio_client = SimpleRecordClient(source=source_name,
                                                     stream_name=stream_name,
                                                     sample_frequency=sample_frequency,
                                                     sample_format=SampleFormat.PA_SAMPLE_FLOAT32LE,
                                                     channels=1,
                                                     target_latency=10 * 1000)
        self._stop_event = threading.Event()

        self.exit_success = None

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        self.join()

    def run(self):
        numpy.seterr(all='raise')

        try:
            with self._pulseaudio_client:
                while not self._stop_event.is_set():
                    self._sample()
        except Exception as e:
            self.exit_success = False
            raise e
        else:
            self.exit_success = True

    def stop(self):
        self._stop_event.set()

    def get_latency(self):
        """Returns the current latency returned by the PulseAudio client."""
        return self._pulseaudio_client.get_latency()

    def _sample(self):
        raise Exception('This function has to be implemented.')
