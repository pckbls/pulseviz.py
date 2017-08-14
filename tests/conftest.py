def pytest_addoption(parser):
    parser.addoption('--minimal-pulseaudio-server',
                     action='store_true',
                     default=None,
                     help='If set, only a bare minimum of PulseAudio modules is loaded required for testing.')
