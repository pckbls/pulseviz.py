**pulseviz** is a small OpenGL-accelerated audio visualizer for PulseAudio written in Python.
Right now it's more or less a proof of concept with little to no features.

![Draft](images/draft.png)

# Dependencies

A recent version of Python 3 (3.5 and above), `PyOpenGL`, `numpy` and (of course) PulseAudio are required.
Both `PyOpenGL` and `numpy` should be part of the official repositories for all major Linux distributions.
Alternatively they can be installed via `pip3`:

    pip3 install -r requirements.txt

# How to use

pulseviz requires you to choose from an audio source and a visualizer type:

    $ ./pulseviz.py
    Usage: ./pulseviz.py <source> <visualizer>

    Available sources:
        alsa_output.pci-0000_00_1b.0.analog-stereo.monitor
        alsa_input.pci-0000_00_1b.0.analog-stereo
        alsa_output.usb-VIA_Technologies_Inc._USB_Audio_Device-00.iec958-stereo.monitor

    Available visualizers:
        waveform
        spectrum
        bands

By default PulseAudio automatically creates a monitor source for each sink which can be used to visualize the audio that you are hearing.
Those sources have a `.monitor` suffix.

# Future goals

* Make visualizers configurable
  * Either via command line switches...
  * ...or via configuration file
* Create more visually appealing visualiziations such as
  * [Spectrogram](https://en.wikipedia.org/wiki/Spectrogram#/media/File:Spectrogram-19thC.png)
  * [Kodi's rotating 3D Spectrum visualizer](http://kodi.wiki/view/File:Fullscreen_music_controls.png).
* Optimize for speed. Smooth 60 frames per seconds with minimal CPU usage are the target.
* Experiment with different digital signal processing algorithms.
