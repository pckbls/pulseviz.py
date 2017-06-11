import pytest
import importlib
import subprocess


@pytest.fixture(scope='session')
def fixture_pulseaudio_library():
    """
    Tries to load the pulseaudio package which depends on libpulse and libpulse-simple
    being installed on the system.
    """

    import pulseaudio
    import pulseaudio.simple_client
    importlib.reload(pulseaudio)
    importlib.reload(pulseaudio.simple_client)
    return pulseaudio


@pytest.fixture(scope='session')
def fixture_pulseaudio_server():
    """
    Makes sure that a PulseAudio server is running.
    If there is already one running (probably the default one started automatically on Desktop systems)
    then that instance is being used. Otherwise a fresh instance is spawned and terminated
    at the end of the test.
    """

    process = subprocess.Popen(['pulseaudio',
                                '--daemonize=no',
                                '-n',
                                '-F', 'tests/data/minimal_server.pa',
                                '--exit-idle-time', '1337',
                                '-v'],
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


@pytest.mark.skip(reason='Does not work right now.')
def test_import_pulseaudio_library(fixture_pulseaudio_library):
    pass


def test_start_pulseaudio_server(fixture_pulseaudio_server):
    pass

