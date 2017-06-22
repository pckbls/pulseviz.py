import threading
import queue
import time
import random
import pytest
from pulseviz.pulseaudio import simple_client


# TODO: Test different sample rates
# TODO: Test different channel settings (mono, stereo)


@pytest.mark.xfail(raises=simple_client.SimpleClientErrorException)
def test_simple_client_failure(simple_client_fixture):
    c = simple_client_fixture
    with c:
        pass


def test_simple_record_client_enter_exit(simple_record_client_fixture):
    c = simple_record_client_fixture
    with c:
        pass


def test_simple_record_client_get_latency(simple_record_client_fixture):
    c = simple_record_client_fixture
    with c:
        latency = c.get_latency()
        assert latency > 0


def test_simple_record_client_read(simple_record_client_fixture):
    c = simple_record_client_fixture
    with c:
        for size in [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]:
            data = c.read(size=size)
            assert len(data) == size
            assert type(data) is list


def test_simple_playback_client_write(simple_playback_client_fixture):
    c = simple_playback_client_fixture
    with c:
        # TODO: 1 and 2 do not work.
        for size in [4, 8, 16, 32, 64, 128, 256, 512, 1024]:
            data = [0 for i in range(0, size)]
            assert len(data) == size
            c.write(data)


@pytest.mark.skip(reason='Too slow.')
def test_read_write(fixture_pulseaudio_server):
    def playback_task():
        # TODO: Use Barrier object to wait for record_task to
        # start recording

        c = simple_client.SimplePlaybackClient(source=b'null', sample_frequency=16)
        with c:
            start_ts = time.time()
            while time.time() - start_ts < 5.0:
                data = [random.randint(0, 255) for _ in range(0, 512)]
                c.write(data)
                c.drain()

    def record_task(result):
        c = simple_client.SimpleRecordClient(source=b'null.monitor', sample_frequency=16)
        with c:
            start_ts = time.time()
            while time.time() - start_ts < 5.0:
                read_data = c.read(size=512)
                if sum(read_data) != 0:
                    result.put(True)
                    return
            result.put(False)

    q = queue.Queue()
    record = threading.Thread(target=record_task, args=(q,), name='record')
    playback = threading.Thread(target=playback_task, name='playback')

    record.start()
    playback.start()

    record.join()
    playback.join()

    assert q.get()
