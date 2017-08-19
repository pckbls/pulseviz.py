import ctypes
import pyglet
from pyglet import gl


# http://www.opengl-tutorial.org/intermediate-tutorials/tutorial-14-render-to-texture/
# http://pydoc.net/glsvg/0.1/glsvg.render_target/ !!!
# https://leovt.wordpress.com/2015/10/04/render-to-texture-with-python-3-and-pyglet/
# https://github.com/leovt/leovt/blob/master/framebuffer.py


class AudioTexture(pyglet.image.Texture):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        buffer_id = gl.GLuint(0)
        gl.glGenFramebuffers(1, ctypes.byref(buffer_id))
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, buffer_id)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
