#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# Small tool that I've written to figure out how to render something onto a texture using pyglet.
#

import ctypes
import pyglet
from pyglet import gl


# Stolen from: https://github.com/fathat/glsvg/blob/master/glsvg/render_target.py#L70
class RenderTarget:
    def __init__(self, texture):
        self.texture = texture
        self.id = gl.GLuint(0)
        gl.glGenFramebuffers(1, ctypes.byref(self.id))
        self.bind()

        gl.glFramebufferTexture2D(
            gl.GL_FRAMEBUFFER,
            gl.GL_COLOR_ATTACHMENT0,
            gl.GL_TEXTURE_2D,
            self.texture.id,
            0)

        self.ok = self.check_status()

        self.unbind()

    def check_status(self):
        status = gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER)
        if status == gl.GL_FRAMEBUFFER_COMPLETE:
            print("Framebuffer complete")
            return True
        else:
            print("Render target error: " + str(status))
            return False

    def bind(self):
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.id)

    def unbind(self):
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

    def __enter__(self):
        self.bind()
        return self

    def __exit__(self, type, value, traceback):
        self.unbind()
        pass


image = pyglet.image.create(100, 100)
render_target = RenderTarget(image.get_texture())
window = pyglet.window.Window()


@window.event
def on_draw():
    window.clear()
    with render_target:
        gl.glColor3f(0.0, 1.0, 0.0)
        gl.glBegin(gl.GL_TRIANGLES)
        gl.glVertex3f(1.0, 0.0, 0.0)
        gl.glVertex3f(0.0, 80.0, 0.0)
        gl.glVertex3f(40.0, 40.0, 0.0)
        gl.glEnd()

    image.blit(0, 0)


@window.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.Q:
        pyglet.app.exit()


pyglet.app.run()
