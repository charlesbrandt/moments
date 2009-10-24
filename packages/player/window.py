"""
A place to customize the default pyglet window object

typically there are common settings for them all.

This is an open version.

*2009.09.24 11:02:43 
"""
import pyglet

class Window(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        pyglet.window.Window.__init__(self, *args, **kwargs)


class Layer(object):
    """
    new layer object

    higher level than a batch
    knows about contents as python objects
    """
    def __init__(self, window, batch=None):
        self.window = window
        if batch is None:
            self.batch = pyglet.graphics.Batch()
        else:
            self.batch = batch
        self.items = []

        self.width = None
        self.height = None
        
        #where we begin relative to parent object
        #all of our items' positions are relative to this:
        self.x = None
        self.y = None

        #place to record last calculated position in the main window:
        self.gx = None
        self.gy = None
        

    def build(self):
        pass

    def get_size(self):
        """
        could also:
        look through all items
        see what their dimensions are
        """
        return (self.width, self.height)

    def apply_window_size(self):
        pass
