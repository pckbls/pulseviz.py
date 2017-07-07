import threading
import queue
import time
import random
import pytest
from pulseviz.pulseaudio import simple_client


# TODO: Test different sample rates
# TODO: Test different channel settings (mono, stereo)


@pytest.fixture()
def fixture_simple_client(fixture_pulseaudio_server, request):
    return simple_client.SimpleClient(name='pulseviz-tests',
                                      stream_name=request.function.__name__)


@pytest.fixture()
def fixture_simple_record_client(fixture_null_sink, request):
    _, source_name = fixture_null_sink
    return simple_client.SimpleRecordClient(source=source_name,
                                            name='pulseviz-tests',
                                            stream_name=request.function.__name__)


@pytest.fixture()
def fixture_simple_playback_client(fixture_null_sink, request):
    sink_name, _ = fixture_null_sink
    return simple_client.SimplePlaybackClient(sink=sink_name,
                                              name='pulseviz-tests',
                                              stream_name=request.function.__name__)


@pytest.mark.xfail(raises=simple_client.SimpleClientErrorException)
def test_simple_client_failure(fixture_simple_client):
    c = fixture_simple_client
    with c:
        pass


def test_simple_record_client_enter_exit(fixture_simple_record_client):
    c = fixture_simple_record_client
    with c:
        pass


def test_simple_record_client_get_latency(fixture_simple_record_client):
    c = fixture_simple_record_client
    with c:
        latency = c.get_latency()
        assert latency > 0


def test_simple_record_client_read(fixture_simple_record_client):
    c = fixture_simple_record_client
    with c:
        for size in [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]:
            data = c.read(size=size)
            assert len(data) == size
            assert type(data) is list


def test_simple_playback_client_write(fixture_simple_playback_client):
    c = fixture_simple_playback_client
    with c:
        # TODO: 1 and 2 do not work.
        for size in [4, 8, 16, 32, 64, 128, 256, 512, 1024]:
            data = [0 for i in range(0, size)]
            assert len(data) == size
            c.write(data)


@pytest.mark.skip(reason='Not implemented yet.')
def test_simple_record_client_no_server(fixture_simple_record_client):
    assert False


@pytest.mark.skip(reason='Not implemented yet.')
def test_simple_playback_client_no_server(fixture_simple_playback_client):
    assert False


@pytest.mark.skip(reason='Not implemented yet.')
def test_simple_record_client_kill_server(fixture_simple_record_client):
    assert False


@pytest.mark.skip(reason='Not implemented yet.')
def test_simple_playback_client_kill_server(fixture_simple_playback_client):
    assert False

