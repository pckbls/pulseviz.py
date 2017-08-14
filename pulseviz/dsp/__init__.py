import threading
import numpy
from ..pulseaudio.simple_client import SimpleRecordClient, SampleFormat


class PulseAudioSignalAnalayzer(threading.Thread):
    """
    An Analyzer interacts with the audio signal received from the PulseAudio server in a separate thread.
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
        self._on_sample_callbacks = []
        self._lock = threading.Lock()

        self.exit_success = None

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        self.join()

    @property
    def lock(self):
        return self._lock

    def run(self):
        numpy.seterr(all='raise')

        try:
            with self._pulseaudio_client:
                while not self._stop_event.is_set():
                    with self.lock:
                        self._sample()
                        for callback in self._on_sample_callbacks:
                            callback()

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

    def on_sample(self, callback):
        """
        Registers a callback function that is called whenever a new sample arrives.
        Inside the on_sample() function you do not have to aquire the data lock.
        """
        self._on_sample_callbacks.append(callback)

    def _sample(self):
        raise Exception('This function has to be implemented.')
