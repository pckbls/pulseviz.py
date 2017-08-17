import ctypes
from pyglet import gl


# The following code is mostly based on Tristam Macdonald's awesome little shader utility library
# licensed under the Boost Software License Version 1.00:
# https://swiftcoder.wordpress.com/2008/12/19/simple-glsl-wrapper-for-pyglet/


class ShaderException(Exception):
    pass


class ShaderCompileException(ShaderException):
    def __init__(self, shader_handle, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Obtain the length of the info log.
        temp = ctypes.c_int(0)
        gl.glGetShaderiv(shader_handle, gl.GL_INFO_LOG_LENGTH, ctypes.byref(temp))

        # Now save the info log in a string.
        buffer = ctypes.create_string_buffer(temp.value)
        gl.glGetShaderInfoLog(shader_handle, temp, None, buffer)
        self._shader_log = buffer.value.decode('ascii')

    def __str__(self):
        return self._shader_log


class ShaderLinkException(ShaderException):
    pass  # TODO: Implement!


class Shader(object):
    def __init__(self, vertex_shader_source, fragment_shader_source):
        self._vertex_shader_source = vertex_shader_source
        self._fragment_shader_source = fragment_shader_source

        self._linked = False
        self._program_handle = gl.glCreateProgram()

    def __enter__(self):
        self.bind()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()

    def bind(self):
        gl.glUseProgram(self._program_handle)

    def unbind(self):
        gl.glUseProgram(0)  # TODO: 0 unbinds all shaders...

    def compile_and_link(self):
        self._compile_and_attach_shader([self._vertex_shader_source.encode('ascii')], gl.GL_VERTEX_SHADER)
        self._compile_and_attach_shader([self._fragment_shader_source.encode('ascii')], gl.GL_FRAGMENT_SHADER)
        self._link()

    def _compile_and_attach_shader(self, shader_sources, shader_type):
        # TODO: Sanitize inputs
        pass

        # Create the shader handle.
        shader_handle = gl.glCreateShader(shader_type)

        # Convert the source strings into a ctypes pointer-to-char array, and upload them.
        # This is deep, dark, dangerous black magick - don't try stuff like this at home!
        src = (ctypes.c_char_p * len(shader_sources))(*shader_sources)
        gl.glShaderSource(
            shader_handle,
            len(shader_sources),
            ctypes.cast(ctypes.pointer(src), ctypes.POINTER(ctypes.POINTER(ctypes.c_char))),
            None
        ),

        # Compile the shader.
        gl.glCompileShader(shader_handle)

        # Retrieve the compile status.
        temp = ctypes.c_int(0)
        gl.glGetShaderiv(shader_handle, gl.GL_COMPILE_STATUS, ctypes.byref(temp))

        # TODO
        if temp.value == gl.GL_TRUE:
            gl.glAttachShader(self._program_handle, shader_handle)
        elif temp.value == gl.GL_FALSE:
            raise ShaderCompileException(shader_handle)
        else:
            raise Exception('This should not happen: {0}'.format(temp.value))

    def _link(self):
        # TODO
        gl.glLinkProgram(self._program_handle)

        # TODO
        temp = ctypes.c_int(0)
        gl.glGetProgramiv(self._program_handle, gl.GL_LINK_STATUS, ctypes.byref(temp))

        # TODO
        if temp.value == gl.GL_TRUE:
            self._linked = True
        elif temp.value == gl.GL_FALSE:
            raise ShaderLinkException()
        else:
            raise Exception('This should not happen: {0}'.format(temp.value))
