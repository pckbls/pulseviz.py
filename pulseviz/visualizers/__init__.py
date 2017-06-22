registry = {}


def visualizer(name):
    def _wrap(cls):
        registry[name] = cls
        return cls
    return _wrap


# TODO: Is there any way to remove this?
from . import waveform, spectrum, bands
