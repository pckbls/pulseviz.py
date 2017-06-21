import sys
from .pulseaudio.simple_client import SimpleRecordClient
from .pulseaudio import pacmd


REFRESH_RATE = 10.0
SAMPLE_SIZE = 2048


def print_help():
    print('Usage: {0} <source> <visualizer>'.format(sys.argv[0]))

    print('\nAvailable sources:')
    for source in pacmd.list_sources():
        print('    {0}'.format(source))

    print('\nAvailable visualizers:')
    for visualizer in ['waveform', 'spectrum', 'bands']:
        print('    {0}'.format(visualizer))

    sys.exit(1)


def main():
    if len(sys.argv) != 3:
        print_help()

    source = sys.argv[1]
    if source not in pacmd.list_sources():
        print_help()

    visualizer_name = sys.argv[2]
    if visualizer_name == 'waveform':
        from .visualizer.waveform import WaveformVisualizer
        visualizer_type = WaveformVisualizer
    elif visualizer_name == 'spectrum':
        from .visualizer.spectrum import SpectrumVisualizer
        visualizer_type = SpectrumVisualizer
    elif visualizer_name == 'bands':
        from .visualizer.bands import BandsVisualizer
        visualizer_type = BandsVisualizer
    else:
        print_help()

    client = SimpleRecordClient(source=source)
    window = visualizer_type(refresh_rate=REFRESH_RATE,
                             sample_size=SAMPLE_SIZE,
                             pulseaudio_client=client)
    window.start()
    window.join()
