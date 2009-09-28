#!/usr/bin/env python
"""
#
# Description:
# take a path
# determine what is there
# loop through contents

need a mode that automatically marks/logs view unless it is skipped
and need a mode where it will only mark when button is pressed.

# By: Charles Brandt [code at contextiskey dot com]
# On: *2009.07.21 03:09:52 
# License:  MIT

# Requires: moments

/c/playlists/code/slideshow.py
/c/python/pyglet/glue/glue/application.py
/c/python/pyglet/glue/glue/layout.py
/c/python/pyglet/glue/glue/widget.py
/c/media/projects/pyglet-todo.txt
"""
import sys, os
import pyglet
from pyglet.clock import schedule_once, unschedule
from pyglet.window import key
from window import Window

#from glue import application
#from glue.layout import Layout, Flow
#from glue.widget import ImageButton, Image

from osbrowser.meta import make_node

class Slideshow(Window):
    def __init__(self, width=None, height=None):
        super(Slideshow, self).__init__(width, height)
        pyglet.clock.unschedule(self.on_draw)
        pyglet.clock.schedule_interval(self.on_draw, 1.0/1.0)

    def make_image_layout(self, image_node):
        #if we don't create a new batch for each layout,
        #then the global application batch will be used
        #and all currenlty loaded layout items (previous, current, next)
        #will show up there
        #regardless of which layout owns the items
        #order is undefined in that case, which causes a chaotic view
        batch = pyglet.graphics.Batch()
        layout = Flow(self, batch)
        layout.update_dimensions()
        #print self.sources[self.position].path
        #print self.sources[self.position].size_path('large')
        try:
            image_path = image_node.path
            button = Image(image_path, batch=layout.batch)
        except:
            print "falling back to thumbnail"
            image_path = image_node.size_path('large')
            button = Image(image_path, batch=layout.batch)
        #button.action = self.go_next_layout
        layout.add_item(button)
        layout.get_dimensions()
        layout.render()
        return layout
    
    def unschedule_all(self):
        """
        unschedule anything that may have been scheduled
        """
        unschedule(self.go_next_layout)
        unschedule(self.go_previous_layout)

    def prep_next_layout(self, dt=0):
        """
        an example of preparing a layout before changing to it
        good for processor/disk i/o intensive operations
        """
        #need to be at the screen resoultion we're going to use for all trials
        #before building
        self.set_fullscreen(fullscreen=self.use_fullscreen)

        if hasattr(self, "previous_layout") and self.previous_layout:
            self.previous_layout.unload()
        if hasattr(self, "last_layout") and self.last_layout:
            self.previous_layout = self.last_layout
        self.next_layout = self.make_image_layout(self.sources[self.position.next()])

        #if you get a GLException(msg):
        #pyglet.gl.lib.GLException: invalid value
        #make sure that the image is not too large for the destination buffer
        #http://groups.google.com/group/pyglet-users/browse_thread/thread/170cdd497e0e37b9
        #self.next_layout = self.make_image_layout(self.sources[self.position].path)


    def prep_previous_layout(self, dt=0):
        """
        go the opposite direction
        """
        #need to be at the screen resoultion we're going to use for all trials
        #before building
        self.set_fullscreen(fullscreen=self.use_fullscreen)

        if hasattr(self, "next_layout") and self.next_layout:
            self.next_layout.unload()
        if hasattr(self, "last_layout") and self.last_layout:
            self.next_layout = self.last_layout
        self.previous_layout = self.make_image_layout(self.sources[self.position.previous()])


    def go_next_layout(self, dt=0):
        """
        this assumes self.next_layout exists
        """
        self.unschedule_all()
        self.change_layout(self.next_layout,
                           fullscreen=self.use_fullscreen)
        self.position.increment()
        self.prep_next_layout()
        #self.clear()
        #self.current_layout.draw()
        if self.loop:
            schedule_once(self.go_next_layout, self.loop_interval)

    def go_previous_layout(self, dt=0):
        """
        this assumes self.next_layout exists
        """
        self.unschedule_all()
        self.change_layout(self.previous_layout,
                           fullscreen=self.use_fullscreen)
        self.position.decrement()
        self.prep_previous_layout()
        if self.loop:
            schedule_once(self.go_previous_layout, self.loop_interval)
                
def main():
    path = ''
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            usage()
        path = sys.argv[1]

    if not path:
        print "No path"
        exit()
        
    app = Slideshow(800, 1000)
    app.use_fullscreen = False
    app.loop_interval = 3

    #path = '/binaries/graphics/incoming/20090521-20090629/'

    node = make_node(path, relative=False)
    node.scan_directory()
    node.scan_filetypes()
    #print node.images
    app.sources = node.images
    app.position = application.Position(len(app.sources))
    #app.position = 7
    #prep first layout:

    #app.prep_next_layout()
    app.next_layout = app.make_image_layout(app.sources[app.position.next()])
    #app.prep_previous_layout()
    app.previous_layout = app.make_image_layout(app.sources[app.position.previous()])
    app.current_layout = app.make_image_layout(app.sources[0])
    app.current_layout.push_handlers()

    pyglet.app.run()
        
if __name__ == '__main__':
    main()

