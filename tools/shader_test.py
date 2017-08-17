#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import pyglet
from pyglet import gl
from pulseviz import shader


vertex_shader_source = '''
#version 120

void main() {
    gl_Position = ftransform();
}
'''

fragment_shader_source = '''
#version 120

void main(void) {
    gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
}
'''

s = shader.Shader(vertex_shader_source=vertex_shader_source,
                  fragment_shader_source=fragment_shader_source)
s.compile_and_link()

window = pyglet.window.Window()


@window.event
def on_draw():
    window.clear()
    gl.glColor3f(0.0, 1.0, 0.0)

    with s:
        gl.glBegin(gl.GL_TRIANGLES)
        gl.glVertex3f(1.0, 0.0, 0.0)
        gl.glVertex3f(0.0, 80.0, 0.0)
        gl.glVertex3f(40.0, 40.0, 0.0)
        gl.glEnd()


@window.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.Q:
        pyglet.app.exit()


pyglet.app.run()
