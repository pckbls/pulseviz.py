from pulseviz.pulseaudio import pacmd


def test_list_sources(fixture_null_sink):
    _, source_name = fixture_null_sink
    result = pacmd.list_sources()
    print(result)
    assert source_name in result
