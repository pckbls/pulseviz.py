import ctypes
from pyglet import gl


# The following code is mostly based on Ian Overgard's glsvg library
# licensed under the DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE Version 2:
# https://github.com/fathat/glsvg


class TextureFrameBufferException(Exception):
    pass


class TextureFrameBuffer(object):
    """
    Small utility class that allows rendering to a texture.
    """

    def __init__(self, texture):
        self._texture = texture

        self._id = gl.GLuint(0)
        gl.glGenFramebuffers(1, ctypes.byref(self._id))

        self.bind()

        gl.glFramebufferTexture2D(
            gl.GL_FRAMEBUFFER,
            gl.GL_COLOR_ATTACHMENT0,
            gl.GL_TEXTURE_2D,
            self._texture.id,
            0
        )
        status = gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER)
        if status != gl.GL_FRAMEBUFFER_COMPLETE:
            raise TextureFrameBufferException('Error: {0}'.format(status))

        self.unbind()

    def __enter__(self):
        self.bind()
        return self

    def __exit__(self, type, value, traceback):
        self.unbind()

    def bind(self):
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self._id)

    def unbind(self):
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
