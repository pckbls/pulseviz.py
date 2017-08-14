#!/usr/bin/env python3

import pulseviz.dsp.sampler
import pulseviz.dsp.fft
import pulseviz.dsp.bands
import time


if __name__ == '__main__':
    analyzer = pulseviz.dsp.octave_bands.OctaveBands(
        source_name='null.monitor',
        sample_size=8192,
        buffer_size=8192,
        window_function='hanning',
        output='psd',
        scaling='log',
        band_frequencies=pulseviz.dsp.bands.calculate_octave_bands(fraction=3)
    )
    analyzer.start()
    time.sleep(30.0)
    analyzer.stop()
    analyzer.join()
