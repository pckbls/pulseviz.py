import subprocess
import re
import pytest


def test_start_pulseaudio_server(fixture_pulseaudio_server):
    process = subprocess.run(['pulseaudio', '--check'])
    assert process.returncode == 0


def test_create_null_sink(fixture_null_sink):
    sink_name, source_name = fixture_null_sink

    process = subprocess.run(['pacmd', 'list-sinks'], stdout=subprocess.PIPE)
    for line in process.stdout.splitlines(keepends=False):
        line = line.decode('ascii')
        if re.match('^[\t]name: <{0}>$'.format(sink_name), line):
            break
    else:
        pytest.fail('Cannot find "{0}" sink.'.format(sink_name))

    process = subprocess.run(['pacmd', 'list-sources'], stdout=subprocess.PIPE)
    for line in process.stdout.splitlines(keepends=False):
        line = line.decode('ascii')
        if re.match('^[\t]name: <{0}>$'.format(source_name), line):
            break
    else:
        pytest.fail('Cannot find "{0}" source.'.format(source_name))
