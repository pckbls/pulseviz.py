import time
import pytest
from . import pulseaudio_server
from .signal_generator import SignalGenerator


@pytest.fixture(scope='session', autouse=True)
def fixture_pulseaudio_server():
    """
    Yields an object which can be used to manipulate the state of a PulseAudio server instance.
    """

    yield pulseaudio_server


@pytest.fixture
def fixture_pulseaudio_server_running(fixture_pulseaudio_server):
    """
    Makes sure that a PulseAudio server is running.
    """

    fixture_pulseaudio_server.start()
    yield fixture_pulseaudio_server


@pytest.fixture
def fixture_null_sink(fixture_pulseaudio_server_running):
    """
    Ensures that there is a null sink and monitor source available.
    """

    sink_name = 'null'
    fixture_pulseaudio_server_running.unload_module_null_sink()
    fixture_pulseaudio_server_running.load_module_null_sink(sink_name)
    yield sink_name, sink_name + '.monitor'
    fixture_pulseaudio_server_running.unload_module_null_sink()


@pytest.fixture
def fixture_signal_generator(fixture_null_sink):
    """
    Returns a SignalGenerator instance that can be used to generate an audio signal.
    """

    sink_name, _ = fixture_null_sink
    sg = SignalGenerator(sink_name=sink_name)
    return sg


@pytest.fixture
def fixture_audio_playback(fixture_signal_generator):
    """
    Makes sure that there is some audio being played to our null sink.
    """

    sg = fixture_signal_generator
    with sg.attach_generator():
        time.sleep(1.0)  # TODO
        yield sg
