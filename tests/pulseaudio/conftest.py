import pytest
import subprocess
from pulseviz.pulseaudio import simple_client


@pytest.fixture(scope='session', autouse=True)
def fixture_pulseaudio_server():
    """
    Makes sure that a PulseAudio server is running.
    If there is already one running (probably the default one started automatically on Desktop systems)
    then that instance is being used. Otherwise a fresh instance is spawned and terminated
    at the end of the test.
    """

    # TODO: Try --start parameter
    # TODO: Try using --daemonize
    # TODO: Pipe log to file and save as artifact in GitLab

    process = subprocess.Popen(['pulseaudio',
                                '--daemonize=no',
                                '-n',
                                '-F', 'tests/data/minimal_server.pa',
                                '--exit-idle-time', '1337',
                                '-vvvv'],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

    try:
        stdout, stderr = process.communicate(timeout=5.0)
    except subprocess.TimeoutExpired:
        # The process is still running which is a good indication that it worked.
        yield True
        process.terminate()
        _, stderr = process.communicate()
        for line in stderr.splitlines(keepends=False):
            print(line.decode('utf-8'))
    else:
        # The process terminated. Let's check if there's another PulseAudio instance running.
        error_msg = b'E: [pulseaudio] pid.c: Daemon already running.'
        if error_msg in stderr.splitlines(keepends=False):
            # Re-use the existing PulseAudio instance for our tests.
            yield True
        else:
            raise Exception('Cannot start PulseAudio server.')


# TODO: Use function scope instead and create a unique null sink
# by appending the test name to it.
@pytest.fixture(scope='session', autouse=True)
def fixture_null_sink(fixture_pulseaudio_server):
    """
    Ensures that there is a null sink and monitor source available.
    """

    sink_name = 'null'
    subprocess.run(['pacmd', 'unload-module', 'module-null-sink'])
    process = subprocess.run(['pacmd', 'load-module', 'module-null-sink', 'sink_name="{0}"'.format(sink_name)])
    assert process.returncode == 0
    yield sink_name, sink_name + '.monitor'
    subprocess.run(['pacmd', 'unload-module', 'module-null-sink'])


@pytest.fixture()
def simple_client_fixture(fixture_pulseaudio_server, request):
    return simple_client.SimpleClient(name='pulseviz-tests', stream_name=request.function.__name__)


@pytest.fixture()
def simple_record_client_fixture(fixture_null_sink, request):
    _, source_name = fixture_null_sink
    return simple_client.SimpleRecordClient(source=source_name, name='pulseviz-tests', stream_name=request.function.__name__)


@pytest.fixture()
def simple_playback_client_fixture(fixture_null_sink, request):
    sink_name, _ = fixture_null_sink
    return simple_client.SimplePlaybackClient(sink=sink_name, name='pulseviz-tests', stream_name=request.function.__name__)
