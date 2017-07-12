import pytest


class FakeLibPulseSimple(object):

    def pa_usec_to_bytes(a, b):
        return 1337

    def pa_simple_new(a, b, c, d, e, f, g, h, i):
        return 1337

    def pa_simple_read(a, data, size, error):
        data[:] = (type(data))(0)  # Yes, this actually works!
        return 0

    def pa_simple_flush(a, b):
        return 0

    def pa_simple_free(a):
        return 0


@pytest.fixture
def fixture_fake_simple_client(monkeypatch):
    """
    Patches the simple_client module so that it does not require a real PulseAudio server to work.
    """

    import pulseviz.pulseaudio.simple_client
    monkeypatch.setattr(pulseviz.pulseaudio.simple_client, '_libpulse_simple', FakeLibPulseSimple)
