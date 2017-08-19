import threading
import numpy
import pyglet
from pyglet import gl
from .. import VisualizerWindow
from ... import shader, texture


# https://gamedev.stackexchange.com/questions/55945/how-to-draw-image-in-memory-manually-in-pyglet
# http://www.opengl-tutorial.org/intermediate-tutorials/tutorial-14-render-to-texture/
# http://pydoc.net/glsvg/0.1/glsvg.render_target/ !!!
# https://leovt.wordpress.com/2015/10/04/render-to-texture-with-python-3-and-pyglet/
# https://github.com/leovt/leovt/blob/master/framebuffer.py


class ShadertoyVisualizerWindow(VisualizerWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._samples_n = self._analyzer.buffer_size
        self._vertex_list = pyglet.graphics.vertex_list(
            self._samples_n,
            ('v2f/dynamic', numpy.zeros(self._samples_n * 2))
        )
        self._lock = threading.Lock()

        self._time = 0.0

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

        # self._image = pyglet.image.load('images/bands.png')
        self._image = pyglet.image.create(512, 2)
        self._texture = self._image.get_texture()
        self._texture_foo_bar = texture.TextureFrameBuffer(self._texture)

    def on_sample(self):
        with self._lock:
            bin_width = 1.0 / self._samples_n
            self._vertex_list.vertices[0::2] = numpy.arange(0, self._samples_n) * bin_width * self._image.width
            # self._vertex_list.vertices[1::2] = (self._analyzer.buffer / 2.0 + 0.5) * self._image.height * 0.5
            self._vertex_list.vertices[1::2] = numpy.ones(self._samples_n)

    def on_update(self, dt):
        self._time += dt

        with self._texture_foo_bar, self._lock:
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
            gl.glBegin(gl.GL_LINE_STRIP)
            for x, y in zip(self._vertex_list.vertices[0::2], self._vertex_list.vertices[1::2]):
                gl.glColor3f(numpy.random.random_sample(), numpy.random.random_sample(), numpy.random.random_sample())
                gl.glVertex2f(x, y)
            gl.glEnd()
            # self._vertex_list.draw(pyglet.gl.GL_LINE_STRIP)

    def on_draw_(self):
        if False:
            self._image.blit(0.0, 0.0, 0.0)
            return
            gl.glBegin(gl.GL_QUADS)
            gl.glVertex2f(0.0, 0.0)
            gl.glVertex2f(1.0 * self.width, 0.0)
            gl.glVertex2f(1.0 * self.width, 1.0 * self.height)
            gl.glVertex2f(0.0, 1.0 * self.height)
            gl.glEnd()

        with self._shader:
            gl.glUniform3f(
                gl.glGetUniformLocation(self._shader._program_handle, b'iResolution'),
                self.width, self.height, 0.0
            )

            gl.glUniform1f(
                gl.glGetUniformLocation(self._shader._program_handle, b'iTime'),
                self._time
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
