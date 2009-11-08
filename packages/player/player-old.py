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

# Requires:
pyglet
moments

"""
import os, sys, re, codecs
import pyglet
from pyglet.window import key

from moments.log import Log
from moments.journal import load_journal

from medialist.sources import Playlist, entries_to_playlist
    
window = pyglet.window.Window(resizable=True, visible=False)

playlist = Playlist(window)

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
            playlist.player.seek(seek)
            playlist.player.play()
        except:
            print "invalid time: %s" % window.user_response
        window.user_response = ''

    #jump to position in playlist
    elif key.symbol_string(symbol) == "TAB":
        try:
            position = int(window.user_response)
            playlist.list_go(position)
        except:
            print "invalid position: %s" % window.user_response
        window.user_response = ''

    #toggle between playing and paused
    elif key.symbol_string(symbol) == "SPACE":
        if playlist.player._playing:
            playlist.player.pause()
        else:
            playlist.player.play()

    #start playing
    elif key.symbol_string(symbol) == "P":
        playlist.player.play()

    #toggle time display
    elif key.symbol_string(symbol) == "O":
        if playlist.show_time:
            playlist.show_time = False
        else:
            playlist.show_time = True

    #toggle jump mode
    elif key.symbol_string(symbol) == "J":
        if playlist.jumping:
            pyglet.clock.unschedule(playlist.jump_next)
            playlist.jumping = False
        else:
            pyglet.clock.schedule_once(playlist.jump_next, 1)
            playlist.jumping = True

    #jump next timestamp in time list
    elif key.symbol_string(symbol) == "N":
        playlist.jump_next(0)

    #add an entry to the the log
    elif key.symbol_string(symbol) == "L":
        playlist.log_current()

    #mark current position
    elif key.symbol_string(symbol) == "M":
        #add current position to jump list... then it can be written to log
        #will be written to log when jumps complete
        time = playlist.player._get_time()
        #print time

        #seconds only
        seconds = int(time)
        if not playlist.jumps:
            playlist.jumps = [ seconds ]
        else:
            #would be better to insert in sequence here... can order that later
            playlist.jumps.append(seconds)
        #playlist.jump_next(0)

        print "added mark: %s" % seconds

    #save an image of current buffer
    elif key.symbol_string(symbol) == "S":
        #this results in the timestamp showing up in the image (if on screen)
        #but is right side up
        time = playlist.player._get_time()
        filename2 = "%04d.png" % (time)
        pyglet.image.get_buffer_manager().get_color_buffer().save(filename2)
        
    elif ((key.symbol_string(symbol) == "RIGHT" and
          key.modifiers_string(modifiers) == "MOD_CTRL") or
          key.symbol_string(symbol) == "PAGEUP"):
        #playing = player._playing
        time = playlist.player._get_time()
        time += 35
        playlist.player.seek(time)
        playlist.player.play()
    elif ((key.symbol_string(symbol) == "LEFT" and
          key.modifiers_string(modifiers) == "MOD_CTRL") or
          key.symbol_string(symbol) == "PAGEDOWN"):
        time = playlist.player._get_time()
        time -= 35
        playlist.player.seek(time)
        playlist.player.play()
    elif key.symbol_string(symbol) == "RIGHT":
        time = playlist.player._get_time()
        time += 5.
        playlist.player.seek(time)
        playlist.player.play()
    elif key.symbol_string(symbol) == "LEFT":
        time = playlist.player._get_time()
        time -= 11
        playlist.player.seek(time)
        playlist.player.play()
    elif key.symbol_string(symbol) == "UP":
        playlist.list_previous()
    elif key.symbol_string(symbol) == "DOWN":
        playlist.list_next()

@window.event
def on_draw():
    window.clear()
    texture = playlist.player.get_texture()
    if texture:
        texture.blit(0, 0)

    if playlist.show_time:
        time = playlist.player._get_time()
        #print time

        #seconds only
        seconds = int(time)
        if str(seconds) != playlist.seconds.text:
            playlist.seconds.text = str(seconds)
        #more detail:
        #label.text = str(time)

        playlist.seconds.draw()

        #doesn't seem to be a way to get the total length of the current
        #media item loaded via the Player object

        #but it is available as source.duration property
        playlist.d.text = " / %s" % int(playlist.duration)
        playlist.d.draw()
                        
def main():
    global playlist

    jumps = []
    start = 0
    source_file = None
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            print __doc__
            sys.exit(1)
        elif '-ss' in sys.argv:
            pos = sys.argv.index("-ss")
            sys.argv.remove("-ss")
            start = int(sys.argv.pop(pos))
        elif '-sl' in sys.argv:
            pos = sys.argv.index("-sl")
            sys.argv.remove("-sl")
            jumps = string_to_jumps(sys.argv.pop(pos))
            source = sys.argv.pop(pos)
            playlist.append( [source, jumps] )
            
        elif '-images' in sys.argv:
            from osbrowser.meta import make_node
            pos = sys.argv.index("-images")
            sys.argv.remove("-images")
            
            #should be relative to this file:
            image_dir = sys.argv.pop(pos)
            node = make_node(os.path.join(os.path.dirname(__file__), image_dir))
            node.scan_directory()
            node.scan_filetypes()
            images = node.images
            for i in images:
                seconds = i.name[:4]
                if int(seconds) not in jumps:
                    jumps.append(int(seconds))
            jumps.sort()

        elif '-m3u' in sys.argv:
            pos = sys.argv.index("-m3u")
            sys.argv.remove("-m3u")
            
            filename = sys.argv.pop(pos)
            f = codecs.open(filename, encoding='utf8')

            for line in f.readlines():
                line = unicode(line)
                if line.startswith('#') or len(line.strip()) == 0:
                    pass
                else:
                    source_file = line.strip()
                    source_file = source_file.replace('"', '')
                    playlist.append( [source_file] )
            f.close

        #*2009.06.18 14:29:41 
        #main function for slist and mlist have been merged
        #could use the same command line option
        #but they do load journals differently

        # playlist that includes jump lists (second lists)
        elif '-slist' in sys.argv:
            pos = sys.argv.index("-slist")
            sys.argv.remove("-slist")
            
            playlist_file = sys.argv.pop(pos)
            pfile = Log(playlist_file)
            pfile.from_file()
            entries = pfile.to_entries()
            pl = entries_to_playlist(entries)
            print len(pl)
            playlist.extend(pl)
            

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
a            """
            pos = sys.argv.index("-mlist")
            sys.argv.remove("-mlist")
            
            playlist_file = sys.argv.pop(pos)
            j = load_journal(playlist_file)
            entries = j

            pl = entries_to_playlist(entries)
            #new_list = condense_and_sort_list(pl)

            #print new_list
            #exit()
            playlist.extend(pl)

        else:
            #get rid of the command argument:
            del sys.argv[0]

            #go through all arguments remaining... could have been passed
            #multiple items via a wildcard
            #print sys.argv
            for path in sys.argv:
                #not sure if we actually want to recurse here
                #or if it would be better to let load source
                #offer the option of launching a new player
                if os.path.isdir(path):
                    for i in os.listdir(path):
                        playlist.append( [os.path.join(path, i)] )
                else:
                    playlist.append ( [path] )
            print playlist

        if "-save" in sys.argv:

            # *2009.08.30 09:58:05 
            # a quick place to add in functionality to save the resulting
            # m3u file
            # might want to generalize this.
            o = file("playlist.m3u", 'w')
            for i in playlist:
                #if re.match('\/c\/media\/binaries', i):
                if i[0].startswith('/c/media/binaries'):
                    i = i[0].replace('/c/media/binaries/music', '/Volumes/Binaries/music')
                    print i
                else:
                    print "NO MATCH: %s" % i[0]
                    i = ''
                if not re.search('JPG', i):
                    o.write(i)
                    o.write('\n')
            exit()
            

    #width=format.width, height=format.height
    window.set_visible(True)
    window.user_response = ''

    #if playlist:
    #    player.playlist = playlist

    #print playlist
    #exit()

    playlist.list_go(0)
    pyglet.app.run()
        
if __name__ == '__main__':
    main()
