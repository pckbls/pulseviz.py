import os
import sys
import pyglet
from .pulseaudio import pacmd
from . import visualizers

# Import all our visualizers so that they get registered even if we do not actually use them.
# from .visualizers import dummy  # noqa
from .visualizers import waveform  # noqa
from .visualizers import spectrum  # noqa
from .visualizers import bands  # noqa
from .visualizers import shadertoy  # noqa


def print_help():
    print('Usage: {0} <source> <visualizer>'.format(os.path.basename(sys.argv[0])))

    print('\nAvailable sources:')
    for source in pacmd.list_sources():
        print('    {0}'.format(source))

    print('\nAvailable visualizers:')
    for visualizer in visualizers.registry.keys():
        print('    {0}'.format(visualizer))

    sys.exit(1)


def main():
    if len(sys.argv) != 3:
        print_help()

    source = sys.argv[1]
    if source not in pacmd.list_sources():
        print_help()

    visualizer_name = sys.argv[2]
    visualizer_type = visualizers.registry.get(visualizer_name)
    if visualizer_type is None:
        print_help()

    def stop():
        print('Stopping...')
        pyglet.app.exit()

    print('Using {0} as audio source.'.format(source))
    print('You can press the [h] key to show a help text.')

    window = visualizer_type(source_name=source, stop_callback=stop)
    window.start()
    pyglet.app.run()
