import time
import pytest
from pulseviz.dsp.fft import FFTAnalyzer


@pytest.mark.parametrize('window_function', [None, 'hanning'])
def test_analyze(fixture_null_sink, fixture_audio_playback, window_function):
    sink_name, source_name = fixture_null_sink

    analyzer = FFTAnalyzer(sample_size=2048,
                           window_function=window_function,
                           source_name=source_name,
                           stream_name='pulseviz-tests')

    with analyzer:
        time.sleep(1.0)

    assert analyzer.exit_success
