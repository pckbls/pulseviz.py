import pytest
import subprocess
import time


def start():
    """Starts a PulseAudio server."""

    if pytest.config.getoption('--minimal-pulseaudio-server') is not None:
        subprocess.run([
            'pulseaudio',
            '-n',
            '-F', 'tests/pulseaudio/data/minimal_server.pa',
            '--exit-idle-time', '1337',
            '--start',
            '-vvvv'
        ])
    else:
        subprocess.run(['pulseaudio', '--start'])

    time.sleep(3.0)

    assert is_running()


def stop(kill=False):
    """Stops (or alternatively kills) all PulseAudio servers."""

    subprocess.run(['pulseaudio', '--kill'])
    time.sleep(3.0)

    if kill:
        subprocess.run(['killall', '-9', 'pulseaudio'])
    time.sleep(3.0)

    assert not is_running()


def is_running():
    """Returns True if there's at least one PulseAudio server running."""

    process = subprocess.run(['pulseaudio', '--check'])
    return process.returncode == 0


def load_module_null_sink(sink_name):
    """Loads a module-null-sink with the given sink name."""

    process = subprocess.run([
        'pacmd',
        'load-module',
        'module-null-sink',
        'sink_name="{0}"'.format(sink_name)
    ])
    assert process.returncode == 0


def unload_module_null_sink():
    """Unloads all module-null-sink modules."""

    subprocess.run(['pacmd', 'unload-module', 'module-null-sink'])
