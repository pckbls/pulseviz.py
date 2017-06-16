import pytest
from pulseviz.pulseaudio import pacmd
from .test_pulseaudio import fixture_pulseaudio_server, fixture_null_sink


def test_list_sources(fixture_null_sink):
    _, source_name = fixture_null_sink
    result = pacmd.list_sources()
    print(result)
    assert source_name in result
