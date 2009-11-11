#!/usr/bin/env python
"""
#
# Description:
# play video files using pyglet

# By: Charles Brandt [code at contextiskey dot com]
# On: *2009.04.29 10:50:56 
# License:  MIT

# Originally based on video.py example included in pyglet source

# based on examples/video.py distributed by pyglet, written by Alex Holkner

*2009.09.18 12:48:03 
# could easily use this to make system calls to a different player of choice
# then this becomes a way to manage your playlists and keep open logs
# of what happens when

# Requires:
pyglet
moments
medialist

*2009.09.18 10:50:03
major refactor
"""
import os, sys, re, codecs
import pyglet
from pyglet.media import Player as PygletPlayer
from pyglet.window import key
from pyglet.gl import *

# Enable alpha blending, required for image.blit.
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

from moments.log import Log
from moments.journal import load_journal
from moments.node import Node, make_node
from moments.sources import Converter, Source, Sources
    
#window = pyglet.window.Window(resizable=True, visible=False)
#start using a generalized Window with default configuration options
from window import Window
window = Window(resizable=True, visible=False)

class Player(object):
    """
    pyglet player specific wrapper to navigate through a Sources list object  
    """
    def __init__(self, window, sources):
        self.player = None

        #need to track this so we know where to play it
        self.window = window

        self.sources = sources

        self.seconds = pyglet.text.Label("0.0",
                                         font_name='Times New Roman',
                                         font_size=24,
                                         #we don't have this yet here:
                                         #x=window.width//5,
                                         #y=window.height-(window.height//5)
                                         x=40, y=20,
                                         anchor_x='center', anchor_y='center')
        self.d = pyglet.text.Label(" / ",
                                   font_name='Times New Roman',
                                   font_size=14,
                                   #we don't have this yet here:
                                   #x=window.width//5,
                                   #y=window.height-(window.height//5)
                                   x=100, y=20,
                                   anchor_x='center', anchor_y='center')
        self.show_time = True

        #duration of the current source item
        self.duration = 0

        self.jump_interval = 5
        self.jumping = False

        self.img = None
        self.previous = None
        self.next = None

        checks = pyglet.image.create(32, 32, pyglet.image.CheckerImagePattern())
        self.background = pyglet.image.TileableTexture.create_for_image(checks)

    def list_previous(self):
        new_position = self.sources.position.previous()
        self.list_go(new_position)

    def list_next(self):
        new_position = self.sources.position.next()
        self.list_go(new_position)

    def jump_next(self, dt=0):
        pyglet.clock.unschedule(self.jump_next)
        if self.sources.current.jumps and not self.sources.current.jumps.position.at_end():
            next = self.sources.current.jumps.go_next()
            self.player.seek(next)
            self.player.play()
            pyglet.clock.schedule_once(self.jump_next, self.jump_interval)
        else:
            self.sources.log_current()
            self.list_next()

    def list_go(self, position=None):
        item = self.sources.go(position)
        if item.jumps.position.at_end():
            item.jumps.position.set(0)
        
        #make sure the previous player is stopped and deleted
        #if it exists:
        if self.player:
            #not sure if we need to remove handlers for this player:
            #self.player.remove_handlers()
            self.player.pause()
            del self.player

        playing = self.load_item(item)

        if playing:
            now_playing = self.sources.now_playing()
            print "Playlist position: %s/%s" % (self.sources.position, len(self.sources))
            print now_playing.render()


    def load_item(self, item):
        """
        this is the place for osbrowser to automatically determine
        path object and create list accordingly
        """

        playing = False

        #make sure the file exists:
        item_node = None
        try:
            item_node = make_node(item.path, relative=False, create=False)
        except:
            print "Item not found: %s" % item.path
            self.list_next()

        if item_node:
            media_type = item_node.find_type()
            print media_type

            #if item is an entry, show it

            #if item is a image file path, show it
            if media_type == "Image":
                if self.img:
                    self.previous = self.img

                if self.next:
                    self.img = self.next
                else:
                    self.img = self.load_image(item_node)
                    
                self.img.anchor_x = self.img.width // 2
                self.img.anchor_y = self.img.height // 2

                window.width = self.img.width
                window.height = self.img.height
                #window.set_visible()
                self.img.blit(window.width // 2, window.height // 2, 0)
                window.flip()

                #this should happen in the directional caller
                self.next = self.load_image(item_node)

                playing = True

            #something we can PLAY: (video or audio)
            elif media_type == "Movie" or media_type == "Sound":
                source = self.load_playable(item.path)
                if source:
                    self.duration = source.duration


                    #make a new one:
                    self.player = PygletPlayer()
                    self.player.on_eos = self.on_eos
                    self.player.queue(source)


                    #until we find out otherwise:
                    self.jumping = False
                    if item.jumps:
                        self.jumping = True
                        self.jump_next()
                    else:
                        self.player.play()

                playing = True

            #if path is a directory, 
            #or another playlist, log, etc.
            #launch new player instance with contents

            else:
                print "Unknown media type, moving on"
                self.list_next()
                playing = False

        return playing    
        
    def load_image(self, item_node):
        """
        take a node, return a pyglet image
        """
        try:
            #image_path = image_node.path
            #button = Image(image_path, batch=layout.batch)

            img = pyglet.image.load(item_node.path).get_texture(rectangle=True)
        except:
            print "falling back to thumbnail"
            image_path = item_node.size_path('large')
            img = pyglet.image.load(image_path).get_texture(rectangle=True)

        return img
    
    def load_playable(self, path):
        """
        accepts a medialist.source.Source item made up of:
        -path
        -jumps
        -entry
        *2009.11.06 14:18:41
        now just takes the path we want to load... all that is needed here
        """

        #should decide if it is a stream here:
        ## #source_file = source_file.replace(' ', '\\ ')
        ## #print source_file
        ## ## try:
        ## if re.match('http:', item[0]):
        ##     source = self.load_stream(item[0])

        ### LOAD STREAM:
        ## #def get(host,port,url):
        ## def load_stream(self, stream):
        ## import urllib2
        ## f = urllib2.urlopen(stream)
        #pyglet does not currently support passing in file like arguments
        #to media.load
        #file:///c/downloads/reference/pyglet/doc/html/api/pyglet.media-module.html#load
        #http://snippets.dzone.com/posts/show/5722
        ##     h = httplib.HTTP(host, port)
        ##     h.putrequest('GET', url)
        ##     h.putheader('Host', host)
        ##     h.putheader('User-agent', 'python-httplib')
        ##     h.endheaders()

        ##     (returncode, returnmsg, headers) = h.getreply()
        ##     if returncode != 200:
        ##         print returncode, returnmsg
        ##         sys.exit()

        ##     f = h.getfile()
        ##     return f.read()


        ## else:
        ##     source = self.load_source(item[0])
        ## ## except:
        ## ##     print "could not load: %s ... skipping" % item[0]
        ## ##     if position < self.list_pos and position != 0:
        ## ##         self.list_pos = position
        ## ##         self.list_previous()
        ## ##     else:
        ## ##         self.list_pos = position
        ## ##         self.list_next()                
        ## ##     return


        try:
            source = pyglet.media.load(path)
        except:
            print "Item path: %s" % path
            exit()
        format = source.video_format
        if not format:
            #print 'No video track in this source.'
            #sys.exit(1)
            self.window.width = 150
            self.window.height = 40
        else:
            self.window.width = format.width
            self.window.height = format.height
        return source

    def on_eos(self):
        self.sources.log_current()
        self.list_next()


sources = Sources()
player = Player(window, sources)
        
@window.event
def on_text(text):
    #global user_response
    window.user_response += text

@window.event
def on_key_press(symbol, modifiers):
    #global user_response
    #quit!
    if (key.symbol_string(symbol) == "Q" or
          key.symbol_string(symbol) == "ESCAPE"):
        exit()

    #jump to position in current media file
    elif key.symbol_string(symbol) == "RETURN":
        try:
            seek = int(window.user_response)
            player.player.seek(seek)
            player.player.play()
        except:
            print "invalid time: %s" % window.user_response
        window.user_response = ''

    #jump to position in playlist
    elif key.symbol_string(symbol) == "TAB":
        try:
            position = int(window.user_response)
            player.list_go(position)
        except:
            print "invalid position: %s" % window.user_response
        window.user_response = ''

    #toggle between playing and paused
    elif key.symbol_string(symbol) == "SPACE":
        if player.player._playing:
            player.player.pause()
        else:
            player.player.play()

    #start playing
    elif key.symbol_string(symbol) == "P":
        player.player.play()

    #toggle time display
    elif key.symbol_string(symbol) == "O":
        if player.show_time:
            player.show_time = False
        else:
            player.show_time = True

    #toggle jump mode
    elif key.symbol_string(symbol) == "J":
        if player.jumping:
            pyglet.clock.unschedule(player.jump_next)
            player.jumping = False
        else:
            pyglet.clock.schedule_once(player.jump_next, 1)
            player.jumping = True

    #jump next timestamp in time list
    elif key.symbol_string(symbol) == "N":
        player.jump_next(0)

    #add an entry to the the log
    elif key.symbol_string(symbol) == "L":
        print "Adding Log"
        player.sources.log_current()

    #mark current position
    elif key.symbol_string(symbol) == "M":
        if player.player:
            #add current position to jump list... then it can be written to log
            #will be written to log when jumps complete
            time = player.player._get_time()
            #print time

            #seconds only
            seconds = int(time)
            player.sources.current.jumps.append(seconds)
            #player.jump_next(0)

            print "added mark: %s" % seconds
        else:
            print "no player to mark"
            
    #save an image of current buffer
    elif key.symbol_string(symbol) == "S":
        #this results in the timestamp showing up in the image (if on screen)
        #but is right side up
        time = player.player._get_time()
        filename2 = "%04d.png" % (time)
        pyglet.image.get_buffer_manager().get_color_buffer().save(filename2)
        
    elif ((key.symbol_string(symbol) == "RIGHT" and
          key.modifiers_string(modifiers) == "MOD_CTRL") or
          key.symbol_string(symbol) == "PAGEUP"):
        #playing = player._playing
        time = player.player._get_time()
        time += 35
        player.player.seek(time)
        player.player.play()
    elif ((key.symbol_string(symbol) == "LEFT" and
          key.modifiers_string(modifiers) == "MOD_CTRL") or
          key.symbol_string(symbol) == "PAGEDOWN"):
        time = player.player._get_time()
        time -= 35
        player.player.seek(time)
        player.player.play()
    elif key.symbol_string(symbol) == "RIGHT":
        time = player.player._get_time()
        time += 5.
        player.player.seek(time)
        player.player.play()
    elif key.symbol_string(symbol) == "LEFT":
        time = player.player._get_time()
        time -= 11
        player.player.seek(time)
        player.player.play()
    elif key.symbol_string(symbol) == "UP":
        player.list_previous()
    elif key.symbol_string(symbol) == "DOWN":
        player.list_next()

@window.event
def on_draw():
    window.clear()
    if player.player:
        texture = player.player.get_texture()
        if texture:
            texture.blit(0, 0)

        if player.show_time:
            time = player.player._get_time()
            #print time

            #seconds only
            seconds = int(time)
            if str(seconds) != player.seconds.text:
                player.seconds.text = str(seconds)
            #more detail:
            #label.text = str(time)

            player.seconds.draw()

            #doesn't seem to be a way to get the total length of the current
            #media item loaded via the Player object

            #but it is available as source.duration property
            player.d.text = " / %s" % int(player.duration)
            player.d.draw()

    elif player.img:
        player.background.blit_tiled(0, 0, 0, window.width, window.height)
        player.img.blit(window.width // 2, window.height // 2, 0)
                        
def main():
    global sources
    
    jumps = []
    start = 0
    source_file = None
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            print __doc__
            sys.exit(1)

        #Some overlap here with sources.Converter methods.
        
        elif '-ss' in sys.argv:
            # play one file starting at -ss position
            pos = sys.argv.index("-ss")
            sys.argv.remove("-ss")
            source = Source()
            start = int(sys.argv.pop(pos))
            source.jumps.append(start)
            path = sys.argv[1]
            source.path = path
            sources.append(source)
            
        elif '-sl' in sys.argv:
            # play one file and jump through all jump positions
            pos = sys.argv.index("-sl")
            sys.argv.remove("-sl")
            source = Source()
            source.jumps.from_comma(sys.argv.pop(pos))
            #jumps = string_to_jumps(sys.argv.pop(pos))
            source.path = sys.argv.pop(pos)
            #playlist.append( [source, jumps] )
            sources.append(source)
            
        elif '-m3u' in sys.argv:
            pos = sys.argv.index("-m3u")
            sys.argv.remove("-m3u")
            
            filename = sys.argv.pop(pos)
            f = codecs.open(filename, encoding='utf8')
            
            #this could also be accomplished with Converter.from_m3u
            #but this is a good introduction to Sources objects
            for line in f.readlines():
                line = unicode(line)
                if line.startswith('#') or len(line.strip()) == 0:
                    pass
                else:
                    source_file = line.strip()
                    source_file = source_file.replace('"', '')
                    source = Source(source_file)
                    sources.append( source )
            f.close

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
            #TODO:
            # way to pass in tags to ignore when loading a journal
            # so that those tags are not included with subsequent entries

            j = load_journal(playlist_file)
            print len(j)

            #condense and sort will change the order of an entry list
            #if there are not statistics to generate
            # i.e. one of each only
            # could export as a m3u instead
            # or have separate options not to sort.
            temp = Sources()
            converter = Converter(temp)
            converter.from_entries(j)
            converter.condense_and_sort(sources)

            #for no condensing:
            #converter = Converter(sources)
            #converter.from_entries(j)
            
        else:
            #files passed in via command line:
            #get rid of the command argument:
            del sys.argv[0]

            #go through all arguments remaining... could have been passed
            #multiple items via a wildcard
            #print sys.argv
            for path in sys.argv:
                if os.path.isdir(path):
                    for i in os.listdir(path):
                        new_path = os.path.join(path, i)
                        source = Source(new_path)
                        sources.append( source )
                else:
                    sources.append( Source(path) )
            #print sources

        if "-save" in sys.argv:
            # should use a converter here for consistency
            
            # *2009.08.30 09:58:05 
            # a quick place to add in functionality to save the resulting
            # m3u file
            # might want to generalize this.
            
            o = file("playlist.txt", 'w')
            for i in sources:
                #if re.match('\/c\/media\/binaries', i):
                if i.path.startswith('/c/media/binaries'):
                    i.path = i.path.replace('/c/media/binaries/music', '/Volumes/Binaries/music')
                    #print i
                else:
                    print "NO MATCH: %s" % i.path
                    #i = ''

                #one last place to filter:
                if not re.search('JPG', i.path):
                    o.write(str(i))
                    #o.write('\n')
            exit()
            

    window.set_visible(True)
    window.user_response = ''

    player.list_go(0)

    pyglet.app.run()
        
if __name__ == '__main__':
    main()
