import time
import pytest
from pulseviz.dsp.sampler import Sampler


@pytest.mark.parametrize('sample_frequency', [44100, 48000, 96000])
def test_analyze(fixture_null_sink, fixture_audio_playback, sample_frequency):
    sink_name, source_name = fixture_null_sink

    analyzer = Sampler(sample_frequency=sample_frequency,
                       sample_size=2048,
                       source_name=source_name,
                       stream_name='pulseviz-tests')

    with analyzer:
        time.sleep(1.0)

    assert analyzer.exit_success
