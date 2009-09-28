"""
A place to customize the default pyglet window object

typically there are common settings for them all.

This is an open version.

*2009.09.24 11:02:43 
"""
import pyglet

class Window(pyglet.window.Window):
    def __init__(self):
        pyglet.window.Window.__init__(self)
