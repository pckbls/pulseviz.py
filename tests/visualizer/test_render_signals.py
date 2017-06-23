import pytest
from pulseviz import visualizers
from .. import signal_generators


@pytest.mark.visualizer
@pytest.mark.skipif(not pytest.config.getoption('--visualizer'),
                    reason='need to specify a visualizer type with --visualizer')
@pytest.mark.skipif(not pytest.config.getoption('--signal-generator'),
                    reason='need to specify a signal generator with --signal-generator')
def test_run_visualizer(fake_simple_record_client):
    visualizer_name = pytest.config.getoption('--visualizer')
    signal_generator_name = pytest.config.getoption('--signal-generator')

    visualizer_type = visualizers.registry.get(visualizer_name)
    if visualizer_type is None:
        pytest.fail('Unknown visualizer')

    if signal_generator_name == 'random':
        generator_func = signal_generators.random_generator
    elif signal_generator_name == 'sine':
        generator_func = signal_generators.sine_generator
    else:
        pytest.fail('Unknown signal generator')

    client = fake_simple_record_client
    client.attach_signal_generator(generator_func)
    window = visualizer_type(refresh_rate=10.0,
                             sample_size=1024,
                             pulseaudio_client=client)
    window.start()
    window.join()
