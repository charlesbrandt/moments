import pyglet
from glue.layout import Layout, Flow
from glue.widget import ImageButton, Image
from glue import application

from moments.journal import log_action
from osbrowser.meta import make_node
from medialist.sources import Sources

log_path = "/media/Other/daily/graphics/"
#log_path = "/c/playlists/daily/graphics/"

def make_image_layout(app, image_node):
    #if we don't create a new batch for each layout,
    #then the global application batch will be used
    #and all currenlty loaded layout items (previous, current, next)
    #will show up there
    #regardless of which layout owns the items
    #order is undefined in that case, which causes a chaotic view
    batch = pyglet.graphics.Batch()
    layout = Flow(app, batch)
    layout.set_dimensions()
    #print self.sources[self.position].path
    #print self.sources[self.position].size_path('large')
    try:
        image_path = image_node.path
        button = Image(image_path, batch=layout.batch)
    except:
        try:
            print "falling back to large"
            image_path = image_node.size_path('large')
            button = Image(image_path, batch=layout.batch)
        except:
            print "falling back to medium"
            image_path = image_node.size_path('medium')
            button = Image(image_path, batch=layout.batch)

    #button.action = self.go_next_layout
    layout.add_item(button)
    layout.node = image_node
    layout.get_dimensions()
    layout.render()
    return layout

class ImageSources(Sources):
    def get_item(self, position=None):
        """
        """
        if position is None:
            return make_image_layout(self.app, self[self.position.position])                
            #return self[self.position.position]
        else:
            return make_image_layout(self.app, self[position])    
            #return self[position]


class CustomImageButton(ImageButton):
    def __init__(self, img, x=0, y=0, action=None, rotation=0, batch=None):
        super(CustomImageButton, self).__init__(img, x, y, rotation=rotation, batch=batch)
        print self.path
        self.node = make_node(self.path)
        self.parent = self.node.parent()
        self.parent.scan_filetypes()
        self.parent.sort_by_paths("Image")

    def default_action(self):
        self.node.log_action(['image', 'view'], self.path, log_in_media=True, outgoing=log_path)

        for i in self.parent.images:
            print i.path
        
        self.app.sources = ImageSources(self.parent.images, self.app)
        ct = 0
        for source in self.app.sources:
            if source.path == self.path:
                self.app.sources.position.position = ct
                #print "found position: %s" % ct
            else:
                #print source.path
                pass
            ct += 1

        # storing osbrowser.nodes, not just paths:
        ## if self.path in self.app.sources:
        ##     print "FOUND PATH"
        ##     self.app.sources.position.position = self.app.sources.index(self.path)
        ## else:
        ##     print "NO PATH"
        ##     print self.app.sources
        #print self.path
        self.app.prep_all()

    def on_mouse_press(self, x, y, button, modifiers):
        #print button, modifiers
        if self.mouse_is_over(x, y):
            self.color = (200, 200, 200)
            self.action()
        else:
            self.color = (255, 255, 255)
    
def make_thumb_layout(app, dir_node):
    #if we don't create a new batch for each layout,
    #then the global application batch will be used
    #and all currenlty loaded layout items (previous, current, next)
    #will show up there
    #regardless of which layout owns the items
    #order is undefined in that case, which causes a chaotic view
    batch = pyglet.graphics.Batch()
    layout = Flow(app, batch)
    layout.set_dimensions()
    #print self.sources[self.position].path
    #print self.sources[self.position].size_path('large')

    dir_node.scan_filetypes()
    dir_node.sort_by_paths("Image")
    #print dir_node.images
    print dir_node.path
    for i in dir_node.images:
        image_path = i.size_path('tiny')
        button = None
        try:
            button = CustomImageButton(image_path, batch=layout.batch)
        except:
            #may not have been created
            #could use osbrowser to create
            try:
                dir_node.make_thumbs()
                button = CustomImageButton(image_path, batch=layout.batch)
            except:
                #or could show a "File Not Found" image in it's place
                print "could not create/find a thumbnail for %s" % i.path
        if button:
            #button.action = self.go_next_layout
            button.path = i.path
            button.app = app
            layout.add_item(button)
    layout.get_dimensions()
    layout.render()
    return layout

class DirectorySources(Sources):
    def get_item(self, position=None):
        """
        """
        if position is None:
            return make_thumb_layout(self.app, self[self.position.position])
        else:
            return make_thumb_layout(self.app, self[position])    
    
