import pytest
import ctypes
from pulseviz.pulseaudio import simple_client


# TODO: Test read_into_buffer


@pytest.fixture()
def fixture_simple_record_client(fixture_null_sink, request):
    _, source_name = fixture_null_sink
    kwargs = {
        'source': source_name,
        'name': 'pulseviz-tests',
        'stream_name': request.function.__name__,
        'sample_frequency': 44100,
        'sample_format': simple_client.SampleFormat.PA_SAMPLE_U8,
        'channels': 1,
        'target_latency': 10 * 1000 * 1000
    }
    return kwargs


@pytest.fixture()
def fixture_simple_playback_client(fixture_null_sink, request):
    sink_name, _ = fixture_null_sink
    kwargs = {
        'sink': sink_name,
        'name': 'pulseviz-tests',
        'stream_name': request.function.__name__,
        'sample_frequency': 44100,
        'sample_format': simple_client.SampleFormat.PA_SAMPLE_U8,
        'channels': 1
    }
    return kwargs


def test_libpulse_simple_not_loadable(monkeypatch):
    def LoadLibrary(_):
        raise OSError('foobar')

    monkeypatch.setattr(ctypes.cdll, 'LoadLibrary', LoadLibrary)

    with pytest.raises(ImportError):
        simple_client._load_libpulse_simple()

    # Now undo the changes and reload the library properly, otherwise some weird side effects may occur.
    monkeypatch.undo()
    simple_client._load_libpulse_simple()


def test_connect_disconnect(fixture_simple_record_client, fixture_simple_playback_client):
    src = simple_client.SimpleRecordClient(**fixture_simple_record_client)
    spc = simple_client.SimplePlaybackClient(**fixture_simple_playback_client)
    for c in [src, spc]:
        assert not c.is_connected()
        with c:
            assert c.is_connected()
        assert not c.is_connected()


def test_call_methods_when_not_connected(fixture_simple_record_client, fixture_simple_playback_client):
    src = simple_client.SimpleRecordClient(**fixture_simple_record_client)
    with pytest.raises(simple_client.SimpleClientException): src.get_latency()  # noqa
    with pytest.raises(simple_client.SimpleClientException): src.flush()  # noqa
    with pytest.raises(simple_client.SimpleClientException): src.read(1)  # noqa

    spc = simple_client.SimplePlaybackClient(**fixture_simple_playback_client)
    with pytest.raises(simple_client.SimpleClientException): spc.get_latency()  # noqa
    with pytest.raises(simple_client.SimpleClientException): spc.flush()  # noqa
    with pytest.raises(simple_client.SimpleClientException): spc.write([0.0])  # noqa
    with pytest.raises(simple_client.SimpleClientException): spc.drain()  # noqa


def test_get_latency(fixture_simple_record_client, fixture_simple_playback_client):
    src = simple_client.SimpleRecordClient(**fixture_simple_record_client)
    with src:
        latency = src.get_latency()
        assert latency > 0

    spc = simple_client.SimplePlaybackClient(**fixture_simple_playback_client)
    with spc:
        latency = spc.get_latency()
        assert latency == 0


@pytest.mark.parametrize('sample_frequency', [44100])
@pytest.mark.parametrize('sample_format', [
    simple_client.SampleFormat.PA_SAMPLE_U8,
    # simple_client.SampleFormat.PA_SAMPLE_S16LE,  # TODO: Enable
    simple_client.SampleFormat.PA_SAMPLE_FLOAT32LE
])
@pytest.mark.parametrize('channels', [1, 2])
def test_read(fixture_simple_record_client, sample_frequency, sample_format, channels):
    fixture_simple_record_client['sample_frequency'] = sample_frequency
    fixture_simple_record_client['sample_format'] = sample_format
    fixture_simple_record_client['channels'] = channels

    if channels != 1:
        with pytest.raises(simple_client.SimpleClientException):
            c = simple_client.SimpleRecordClient(**fixture_simple_record_client)
    else:
        c = simple_client.SimpleRecordClient(**fixture_simple_record_client)
        with c:
            for size in [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]:
                data = c.read(size=size)
                assert len(data) == size
                assert data[0] is not None


def test_write_and_drain(fixture_simple_playback_client):
    c = simple_client.SimplePlaybackClient(**fixture_simple_playback_client)
    with c:
        # TODO: 1 and 2 do not work for some reason. Test this?
        for size in [4, 8, 16, 32, 64, 128, 256, 512, 1024]:
            data = [0 for i in range(0, size)]
            assert len(data) == size
            c.write(data)

        c.drain()


def test_no_server_available(fixture_pulseaudio_server_running,
                             fixture_simple_playback_client, fixture_simple_record_client):
    server = fixture_pulseaudio_server_running
    src = simple_client.SimpleRecordClient(**fixture_simple_record_client)
    spc = simple_client.SimplePlaybackClient(**fixture_simple_playback_client)

    server.stop()
    for c in [spc, src]:
        with pytest.raises(simple_client.PulseAudioException):
            with c: pass  # noqa


def test_simple_record_client_kill_server_while_connected(fixture_pulseaudio_server_running,
                                                          fixture_simple_record_client):
    server = fixture_pulseaudio_server_running
    src = simple_client.SimpleRecordClient(**fixture_simple_record_client)

    with src:
        server.stop(kill=True)
        with pytest.raises(simple_client.PulseAudioException):
            src.flush()


def test_simple_playback_client_kill_server_while_connected(fixture_pulseaudio_server_running,
                                                            fixture_simple_playback_client):
    server = fixture_pulseaudio_server_running
    spc = simple_client.SimplePlaybackClient(**fixture_simple_playback_client)

    with spc:
        server.stop(kill=True)
        with pytest.raises(simple_client.PulseAudioException):
            spc.flush()
