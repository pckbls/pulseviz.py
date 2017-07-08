import pytest
from pulseviz.pulseaudio import pacmd


def test_list_sources_pacmd_not_found(monkeypatch):
    import subprocess

    original_Popen = subprocess.Popen

    def Popen(args, **kwargs):
        args[0] = 'pacmd_does_not_exist_on_the_system'
        return original_Popen(args, **kwargs)

    monkeypatch.setattr(subprocess, 'Popen', Popen)

    with pytest.raises(pacmd.PACmdException):
        pacmd.list_sources()


def test_list_sources(fixture_null_sink):
    _, source_name = fixture_null_sink
    result = pacmd.list_sources()
    print(result)
    assert source_name in result
