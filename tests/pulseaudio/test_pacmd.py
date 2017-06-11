import pytest
from pulseviz.pulseaudio import pacmd
from .test_pulseaudio import fixture_pulseaudio_server


def test_get_sources(fixture_pulseaudio_server):
    pacmd.get_sources()

