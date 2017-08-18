import threading
import requests
import pyglet
from pyglet import gl
import numpy
from . import visualizer, Visualizer, VisualizerWindow
from ..dsp.sampler import Sampler
from .. import shader


API_KEY = 'TODO'


class ShadertoyVisualizerWindow(VisualizerWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with open('pulseviz/shader/shadertoy/vertex_main.glsl') as f:
            vertex_shader_source = f.read()

        with open('pulseviz/shader/AudioSurf.glsl') as f:
            fragment_shader_source = f.read()

        self._shader = shader.Shader(
            vertex_shader_source=vertex_shader_source,
            fragment_shader_source=fragment_shader_source
        )

        try:
            self._shader.compile_and_link()
        except shader.ShaderException as e:
            print('Fragment shader source:\n')
            for i, line in enumerate(fragment_shader_source.splitlines()):
                print('{0}: {1}'.format(i+1, line))
            print('')
            raise e

        self._image = pyglet.image.load('images/bands.png')
        self._texture = self._image.get_texture()

    def on_sample(self):
        pass

    def on_update(self, dt):
        pass

    def on_draw_(self):
        if False:
            gl.glBegin(gl.GL_QUADS)
            gl.glVertex2f(0.0, 0.0)
            gl.glVertex2f(1.0 * self.width, 0.0)
            gl.glVertex2f(1.0 * self.width, 1.0 * self.height)
            gl.glVertex2f(0.0, 1.0 * self.height)
            gl.glEnd()

            self._image.blit(0.0, 0.0, 0.0)

            return

        with self._shader:
            gl.glUniform3f(
                gl.glGetUniformLocation(self._shader._program_handle, b'iResolution'),
                self.width, self.height, 0.0
            )

            gl.glUniform1f(
                gl.glGetUniformLocation(self._shader._program_handle, b'iTime'),
                1337.0
            )

            gl.glUniform2f(
                gl.glGetUniformLocation(self._shader._program_handle, b'ifFragCoordOffsetUniform'),
                0.0, 0.0
            )

            gl.glActiveTexture(gl.GL_TEXTURE0 + 0)
            gl.glBindTexture(self._texture.target, self._texture.id)
            gl.glUniform1i(
                gl.glGetUniformLocation(self._shader._program_handle, b'iChannel0'),
                0
            )

            # TODO: I cannot explain why we have to use -1.0 here...
            # Actually we'd want to use 0.0 but if we do so, only the top-right corner
            # of the screen is drawn, lol..
            pyglet.graphics.draw(
                4, gl.GL_QUADS,
                ('0g2f', [
                    -1.0, -1.0,
                    1.0 * self.width, -1.0,
                    1.0 * self.width, 1.0 * self.height,
                    -1.0, 1.0 * self.height
                ])
            )


@visualizer(name='shadertoy')
class WaveformVisualizer(Visualizer):
    ANALYZER_TYPE = Sampler
    VISUALIZER_WINDOW_TYPE = ShadertoyVisualizerWindow
    WINDOW_TITLE = 'Shadertoy Visualizer'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _setup_analyzer(self):
        self._analyzer_kwargs['sample_size'] = 512
        super()._setup_analyzer()

    def _setup_window(self):
        super()._setup_window()

    def start(self, **kwargs):
        self._analyzer.on_sample(self._window.on_sample)
        pyglet.clock.schedule_interval(self._window.on_update, 1 / 10)
        super().start(**kwargs)
