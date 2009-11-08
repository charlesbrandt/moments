#!/usr/bin/env python
"""
#
# Description:
# take a path
# display thumbnails

need a mode that automatically marks/logs view unless it is skipped
and need a mode where it will only mark when button is pressed.

# By: Charles Brandt [code at contextiskey dot com]
# On: *2009.07.23 02:03:15 
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

from glue import application
from glue.layout import Layout, Flow
from glue.widget import ImageButton, Image

from osbrowser.meta import make_node
from scenes import make_thumb_layout, DirectorySources, log_path
from moments.tags import Tags

class Browser(application.Slideshow):
    def __init__(self, path, width=None, height=None):
        super(Browser, self).__init__(1000, 700)
        self.use_fullscreen = False
        self.loop_interval = 3

        #path = '/binaries/graphics/incoming/20090521-20090629/'
        self.node = make_node(path, relative=False)
        self.node.scan_filetypes()
        
        self.sources = DirectorySources(self.node.sub_directories, self)
        self.prep_all()

        self.current_tags = None
        pyglet.clock.schedule_interval(self.on_draw, 1.0/1.0)

    def log_click(self):
        pass

    def on_key_press(self, symbol, modifiers):
        #every layout should have a way out
        if symbol == key.ESCAPE:
            exit()
        elif key.symbol_string(symbol) == "RIGHT":
            self.go_next_layout()
        elif key.symbol_string(symbol) == "LEFT":
            self.go_previous_layout()
        elif key.symbol_string(symbol) == "RETURN":
            # this enables jumping to different position if not in text entry
            ## try:
            ##     self.sources.position.position = int(self.user_response)-1
            ##     self.prep_next_layout()
            ##     self.go_next_layout()
            ## except:
            ##     print "invalid position: %s" % self.user_response
            self.current_tags = Tags().from_spaced_string(self.user_response)
            self.user_response = ''
        elif key.symbol_string(symbol) == "UP":
            #self.current_layout
            self.sources = DirectorySources(self.node.sub_directories, self)
            self.prep_all()
            
        elif key.symbol_string(symbol) == "DOWN":
            cur_source = self.sources[int(self.sources.position)]
            #node = make_node(self.sources)
            if self.current_tags:
                cur_source.log_action(self.current_tags, self.path, log_in_media=True, outgoing=log_path)
            else:
                cur_source.log_action(['image', 'view'], self.path, log_in_media=True, outgoing=log_path)

        # enable if not in tagging mode (text input)
        # and want to be able to play automaticall
        elif key.symbol_string(symbol) == "O":
            if self.show_position:
                self.show_position = False
            else:
                self.show_position = True
        elif symbol == key.P:
            if self.loop:
                unschedule(self.go_next_layout)
                self.loop = False
            else:
                schedule_once(self.go_next_layout, 3)
                self.loop = True

def main():
    path = ''
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            usage()
        elif '-mlist' in sys.argv:
            """
            this is a standard journal file that contains media playback entries
            can parse these based on directory
            or based on file

            if directory,
                merge all files into a journal
                osbrowser.node.create_journal

            otherwise
                just open it as a journal file
            """
            pos = sys.argv.index("-mlist")
            sys.argv.remove("-mlist")
            
            playlist_file = sys.argv.pop(pos)
            j = load_journal(playlist_file)
            entries = j
            pl = entries_to_playlist(entries)

            new_list = condense_and_sort_list(pl)
            #print new_list
            #exit()
            playlist.extend(new_list)
        else:
            path = sys.argv[1]

    if not path:
        print "No path"
        exit()

        
    app = Browser(path)
    pyglet.app.run()
        
if __name__ == '__main__':
    main()

