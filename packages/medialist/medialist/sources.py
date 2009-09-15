import os
from moments.journal import Journal, load_journal
from moments.timestamp import Timestamp
from moments.moment import Moment
from moments.association import Association

class Position(object):
    """
    very similar to a MediaList object here

    but we just want to hold a position
    and length

    from this we can determine the number for previous, next
    and also add increment and decrement options

    loop could be here instead
    
    """
    def __init__(self, length, position=0):
        self.position = position
        self.length = length

    def __int__(self):
        return self.position

    def increment(self):
        """
        changes the actual position variable
        """
        if self.position+1 >= self.length:
            self.position = 0
        else:
            self.position += 1
        return self.position

    def decrement(self):
        """
        changes the actual position variable
        """
        if self.position-1 < 0:
            self.position = self.length-1
        else:
            self.position -= 1
        return self.position
    
    def next(self):
        """
        gives the position for the next item
        but does not actually increment the position
        """
        if self.position+1 >= self.length:
            return 0
        else:
            return self.position+1

    def previous(self):
        """
        gives the position for the next item
        but does not actually increment the position
        """
        if self.position-1 < 0:
            return self.length-1
        else:
            return self.position-1


class Converter(object):
    def __init__(self, path, type="m3u"):
        """
        accept a path as the source
        generate the corresponding Sources object
        """
        self.path = path
        self.type = type

    def from_m3u(self, filename=None):
        if not filename:
            filename = self.source
        #try:
        f = codecs.open(filename, encoding='latin_1')
        #f = open(filename)

        for line in f.readlines():
            line = unicode(line)
            if line.startswith('#') or len(line.strip()) == 0:
                pass
            else:
                self.append(line.strip())
        f.close
        ## except:
        ##     self = []
        ##     raise "trouble loading m3u: %s" % filename

    def from_copy_all_urls(self, data):
        """
        parse a buffer that contains output from copy all urls as a list

        for now skipping title lines... will need those for export
        """
        
        for line in data.splitlines():
            if line.startswith('http://') or line.startswith('/'):
                self.append(line.strip())

    def from_journal(self, journal, tags=[], updates=[], local_path=None):
        """
        filter_and_update
        filter journal based on tags (union)

        apply updates (filters) to all items in all entries

        create a new journal from filtered entries

        journal2medialist

        """
        #m = MediaList(item_type='nodes', prioritize=True)
        self.item_type='nodes'
        self.prioritize=True

        entries = journal.union_tags(tags)
        #entries.reverse()

        #normalize/filter all of the data first...
        #as the system changes, so do the paths
        new_entries = []
        for e in entries:
            filtered_data = ''
            for line in e.data.splitlines():
                if line:
                    [ line ] = multi_filter( [line], updates)
                    #[ line ] = multi_filter( [line], path_updates)
                    if line:
                        filtered_data += line + '\n'

            e.data = filtered_data
            new_entries.append(e)

        #make a new journal with normalized/filtered data
        j2 = Journal()
        j2.from_entries(new_entries)

        #now, create a media list based on the frequency of items in j2
        ilist = j2.datas.frequency_list()
        ilist.sort()
        ilist.reverse()
        for i in ilist:
            #could possibly be more than one file listed in an entry,
            #so other lines will be included
            for line in i[1].splitlines():
                try:
                    if local_path:
                        tnode = make_node(line, local_path=local_path)
                    else:
                        tnode = make_node(line)
                except:
                    tnode = None
                    print "skipping item: %s" % i[1]
                if tnode:
                    self.add_item(tnode)

        #return m
        #m = journal2medialist(j2)
        #return self


    def to_file(self, filename=None):
        """ Default way to save a file """
        #self.to_m3u(filename)
        #sf = filename + "-sorted"
        
        sf = filename
        f = open(sf, 'w')
        for i in self:
            f.write(i)
            f.write('\n')
        f.close()

    def to_links(self, prefix='/dir'):
        links = ''
        for i in self:
            obj = self.get_object(i)
            links += url_for(obj.custom_relative_path(prefix=prefix), qualified=True)
            links += "\r\n"
        return links

    def to_m3u(self, remote=False):
        m3u = "#EXTM3U\r\n"
        for i in self:
            obj = self.get_object(i)
            length = 0
            artist = ""
            title = os.path.basename(i)
            m3u += "#EXTINF:%s,%s - %s\r\n" % (length, artist, title)
            if remote:
                m3u += url_for(obj.custom_relative_path(prefix="/sound"), qualified=True)
            else:
                m3u += i
                
            m3u += "\r\n"
        return m3u

    def to_xspf(self, filename=None):        
        xspf = StringIO.StringIO("Hello")
        xml = XmlWriter(xspf, indentAmount='  ')

        xml.prolog()
        xml.start('playlist', { 'xmlns': 'http://xspf.org/ns/0/', 'version': '1' })
        xml.start('trackList')

        for line in self:
            #line = line.rstrip('\n')

            url = None
            if line.startswith('http://'):
                url = line
            else:
                obj = self.get_object(line)
                if obj:
                    url = url_for(obj.custom_relative_path(prefix="/sound"), qualified=True)
                    #url = url_for(url_escape(obj.custom_relative_path(prefix="/sound")), qualified=True)
                #url = 'file://' + urllib.pathname2url(line)

            if url:
                xml.start('track')
                xml.elem('location', url)
                xml.elem('title', os.path.basename(line))
                #if options.add_annotation:
                #        xml.elem('annotation', createAnnotation(url))

                xml.end() # track

        xml.end() # trackList
        xml.end() # playlist
        
        xspf.seek(0)
        return xspf.read()




#could also consider this a collection of layouts
#sources?  scenes?
class Sources(list):
    """
    this is a list of layouts for our current position
    can use browser to switch between the layouts as normal

    also has a concept of siblings.
    These should just be links of sorts (file path, tags, etc).
    If we navigate to them, can change the point

    also has one parent
    and a list of children.

    similar in concept to a Node on a filesystem
    but keeping it separate to keep it simpler.

    *2009.08.09 17:00:12
    important to remember that for performance
    we don't want to have any more than the current, previous and next layout
    in memory at a time

    therefore this needs to know how to load a layout based on the contents
    and content type

    *2009.08.09 17:02:44
    although, for simple layouts it may be acceptable to load them all into
    memory
    (as in breathe.py)
    """
    def __init__(self, items, app):
        list.__init__(self)
        self.extend(items)
        
        self.app = app
        
        self.parent = None
        self.children = []
        #should include link/index to self.
        self.siblings = []
        self.view = "filesystem"
        self.position = Position(len(self))

    #refactor todo
    #this is what should be overridden in subclasses and called by app
    #not get_item
    #it can call get_item though
    def get_layout(self, position=None):
        pass

    def get_item(self, position=None):
        """
        this should be over-ridden for different instances / subclasses.
        """
        #when over-riding, can do something like the following to generate
        #a layout on the fly
        #self.make_thumb_layout(self.sources[int(self.position)])
        #return make_thumb_layout(self.app, self[position])
        print "Position: %s" % position
        if position is None:
            print self.position.position
            return self[self.position.position]
        else:
            return self[position]

    def get_previous(self):
        return self.get_item(self.position.previous())

    def get_next(self):
        return self.get_item(self.position.next())


import pyglet
from pyglet.media import Player
import re


def jumps_to_string(jumps):
    temp = []
    if jumps:
        for j in jumps:
            if j not in temp:
                temp.append(str(j))
    else:
        temp = ["0"]
    jump_string = ','.join(temp)
    return jump_string

def string_to_jumps(string):
    temps = string.split(',')
    jumps = []
    for j in temps:
        try:
            jumps.append(int(j))
        except:
            print "could not convert %s to int from: %s" % (j, string)
    return jumps
    

def make_key(i):
    """
    convert a playlist item
    (that can have up to 3 elements... file, times, entry)
    into an item suitable for a key in a dictionary
    """
    if len(i) >= 2:
        key = ( i[0], tuple(i[1]) )
    elif len(i) == 1:
        key = ( i[0] )
    return key
    

def condense_and_sort_list(playlist):
    """
    whatever is in the list,
    count the number of times items show up in the list
    (return the frequency of those items)
    and sort items by that frequency
    and return a condesed list in that order
    """
    ## freq = Association()
    ## for i in pl:
    ##     freq.associate(i, i[0])
    ## item_lists = freq.items_by_frequency()
    ## new_list = []
    ## #now have a list of:
    ## #[ [file_path, list_of_original_playlist_items], ..]
    ## for i in item_lists:
    ##     longest = ['', []]
    ##     for playlist_item in i[1]:
    ##         if len(playlist_item[1]) >= len(longest[1]):
    ##             longest = playlist_item
    ##     #print len(longest[1])
    ##     new_list.append(longest)
    tally = {}

    #at this point we will be losing any entry associated
    #in order to condense
    #this will also lose any tag data
    for i in playlist:
        key = make_key(i)
        
        if tally.has_key(key):
            tally[key] += 1
        else:
            tally[key] = 1

    #get the keys and values
    items = tally.items()

    #make sure main items are lists instead of default tuple returned by dict
    new_items = []
    for i in items:
        new_items.append( list(i) )
    items = new_items
    
    #condense items here:
    condensed = items[:]
    for i in items:
        if len(i[0]) > 1:
            #could be more than one c that has i as subset...
            #should stop after one
            #(hence using 'while' instead of 'for')
            match = False
            pos = 0
            while not match:
                c = condensed[pos]
                if (c[0][0] == i[0][0]) and (len(c[0]) > 1):
                    #both have times
                    #check if either is a subset of the other
                    cset = set(c[0][1])
                    iset = set(i[0][1])
                    if len(cset.difference(iset)) == 0:
                        #same set!
                        #could be the same item
                        pass
                    elif cset.issubset(iset):
                        #update tally i in condensed
                        pos = condensed.index(i)
                        condensed[pos][1] += c[1]
                        print "found subset: %s of: %s. current length: %s" % ( cset, iset, len(condensed))
                        condensed.remove(c)
                        print "new length: %s" % len(condensed)
                        match = True
                    elif iset.issubset(cset):
                        #update tally i in condensed
                        pos = condensed.index(c)
                        condensed[pos][1] += i[1]
                        print "found subset: %s of: %s. current length: %s" % ( iset, cset, len(condensed))
                        condensed.remove(i)
                        print "new length: %s" % len(condensed)
                        match = True
                    else:
                        print "times didn't match"
                pos += 1
                if pos >= len(condensed):
                    #maybe no match, exit while loop
                    match = True
                    
                       
    items = condensed
    
    #need to sort based on second item in the list, not the first...
    #not sure how to do this with sort... I know there is a better way than
    #this
    #swap positions:
    new_items = []
    for i in items:
        new_items.append( (i[1], i[0]) )

    new_items.sort()
    new_items.reverse()

    items = []
    for i in new_items:
        items.append( i[1] )

    for i in playlist:
        key = make_key(i)
        if key in items:
            #replace key with i
            pos = items.index(key)
            items[pos] = i
        #sorted_i = ( i[0], tuple(i[1]))

    new_items = []
    for i in items:
        if len(i) > 1:
            times = list(i[1])
            times.sort()
            i[1] = times
        new_items.append(i)
        
    #print items
    #exit()
    return new_items

def entries_to_playlist(entries):
    """
    take a list of moments/entries
    for each line in the entry
    see if it will work as a playlist item
    add if so
    """
    playlist = []
    for e in entries:
        for line in e.data.splitlines():
            if re.search("\ -sl\ ", line):
                #this requires the first 3 items to be:
                # # -sl [nums] [file]
                # otherwise parts will be off
                # see replace.txt
                parts = line.split(' ', 3)
                try:
                    sl_pos = parts.index('-sl')
                except:
                    print "SL found, but incorrect format:"
                    print e.render()
                    exit()
                jumpstr = parts[sl_pos+1]
                jumps = string_to_jumps(jumpstr)
                try:
                    source_file = parts[sl_pos+2]
                except:
                    print "no source file in parts: %s" % parts
                    print line
                    print
                    
                #get rid of surrounding quotes here
                source_file = source_file.replace('"', '')
                
                playlist.append( [source_file, jumps, e] )
            elif re.search("-ss", line):
                continue
            elif line.strip():
                source_file = line.strip()
                if re.match('^media', source_file):
                    source_file = source_file.replace('media/', '')
                    source_file = '/c/' + source_file

                playlist.append( [source_file, [], e] )

    playlist = condense_and_sort_list(playlist)
    return playlist

    

class Playlist(list):
    """
    playlist for pyglet media
    playlists are:
    [ [source, [jumps_as_list], [original_source_entry]], ....  ]

    this playlist is used in /c/playlists/player.py

    TODO:
    subclass Sources for that functionality
    keep pyglet specific functionality here
    """
    def __init__(self, window, playlist=[], jumps=None):
        #PygletPlayer.__init__(self)

        self.extend(playlist)
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
        self.show_time = False

        self.jump_interval = 5
        self.jumping = False
        self.jumps = jumps
        self.jump_pos = 1
        
        #position in playlist
        self.list_pos = 0
        #self.playlist = playlist
        self.first_play = True

        self.player = None

        #need to track this so we know where to play it
        self.window = window

        #duration of the current source item
        self.duration = 0
        
    def list_go(self, position=None):
        if position is None:
            position = self.list_pos
        item = self[position]
        ## try:
        if re.match('http:', item[0]):
            source = self.load_stream(item[0])
        else:
            source = self.load_source(item[0])
        ## except:
        ##     print "could not load: %s ... skipping" % item[0]
        ##     if position < self.list_pos and position != 0:
        ##         self.list_pos = position
        ##         self.list_previous()
        ##     else:
        ##         self.list_pos = position
        ##         self.list_next()                
        ##     return

        self.duration = source.duration
        
        #just in case it was passed in and has not been set yet:
        self.list_pos = position

        #now we need to make sure the previous player is stopped and deleted
        #if it exists:
        if self.player:
            #not sure if we need to remove handlers for this player:
            #self.player.remove_handlers()
            self.player.pause()
            del self.player

        self.player = Player()
        self.player.on_eos = self.on_eos
        self.player.queue(source)

        #until we find out otherwise:
        self.jumping = False

        if len(item) > 1 and item[1]:
            self.jumps = item[1]
            self.jumping = True
            self.jump_next(0)
        else:
            self.player.play()

        now_playing = self.now_playing()
        print "Playlist position: %s/%s" % (self.list_pos, len(self))
        print now_playing.render()
        
    def list_previous(self):
        self.jump_pos = 0
        new_position = self.list_pos - 1
        #self.list_pos -= 1
        if new_position < 0:
            #can either loop or exit
            #exit()
            new_position = len(self)-1
        self.list_go(new_position)

    def list_next(self):
        self.jump_pos = 0
        new_position = self.list_pos + 1
        #self.list_pos += 1
        if new_position >= len(self):
            #can either loop or exit
            #exit()
            new_position = 0
        self.list_go(new_position)

    def jump_next(self, dt):
        pyglet.clock.unschedule(self.jump_next)
        if self.jumps and (self.jump_pos < len(self.jumps)):
            #next = self.jumps.pop(0)
            next = self.jumps[self.jump_pos]
            self.jump_pos += 1
            self.player.seek(next)
            self.player.play()
            pyglet.clock.schedule_once(self.jump_next, self.jump_interval)
        elif len(self):
            self.log_current()
            self.list_next()

    #log that a play was just completed
    def log_current(self):
        j = Journal()
        now = Timestamp(now=True)
        log_name = os.path.join('daily/transfer' , now.filename())
        j.from_file(log_name)
        cur_item = self[self.list_pos]
        if len(cur_item) > 2:
            entry = cur_item[2]
            tags = entry.tags
        else:
            tags = []
        if self.jumps:
            j.make_entry("# -sl %s %s" % (jumps_to_string(self.jumps), cur_item[0]), tags=tags)
        else:
            j.make_entry(cur_item[0], tags=tags)
        j.to_file()

    def now_playing(self):
        """
        return an entry for what is playing
        """
        moment = Moment()
        cur_item = self[self.list_pos]
        if len(cur_item) > 2:
            entry = cur_item[2]
            moment.tags = entry.tags
        else:
            moment.tags = []
        if self.jumps:
            moment.data = "# -sl %s %s" % (jumps_to_string(self.jumps), cur_item[0])
        else:
            moment.data = cur_item[0]

        return moment


    def load_source(self, source_file):
        #source_file = source_file.replace(' ', '\\ ')
        #print source_file

        try:
            source = pyglet.media.load(source_file)
        except:
            print source_file
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


    #def get(host,port,url):
    def load_stream(self, stream):
        """
        a python like wget or curl -O function
        """
        import urllib2
        f = urllib2.urlopen(stream)

        #pyglet does not currently support passing in file like arguments
        #to media.load
        #file:///c/downloads/reference/pyglet/doc/html/api/pyglet.media-module.html#load

        source = pyglet.media.load(file=f, streaming=True)
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
        self.log_current()
        self.list_next()

