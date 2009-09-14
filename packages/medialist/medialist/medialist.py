#*2008.12.10 07:13:33
# separate from Directories now, no dependency on what is stored
# as long as it renders a unique path

#*2008.11.17 13:13:20
# Media lists and Directorys are very similar
# and reference each other often
# not sure if they can be merged
# but if nothing else need to be together for import loops

import os
import random
import subprocess

import StringIO
import re, os, urllib

import codecs

from datetime import datetime

#for XmlWriter
import xml.sax.saxutils as saxutils 

from filters import path_updates

#from webhelpers.html import url_escape
from routes import url_for

from osbrowser.meta import make_node
from moments.journal import Journal

class MediaList(list):
    """
    aka playlist

    can easily check for the existence of a file in a list

    able to load the node (or subclass) python objects

    should also be able to return the list sorted by different criteria
    (order added, filename, common item metadata, creation, last access)

    should be able to export to / import from common formats (m3u)

    media list could use multiple inheritance to inherit from Node too
    this is not always necessary though
    will always be a list
    will only be a Node if there is a file involved
    in that case we can just use path to initiate a Node object to represent
    ourself.

    2008.12.09 21:54:17
    would like this to not be dependent on osbrowser

    should be able to pass in any list of objects if desired
    then use the interface to make it act like a playlist

    this means it will usually be paths,
    but may have cases where it's python objects.

    2008.12.10 06:34:33
    in case of a list of objects, should be ok to require internal list format
    to be a list of strings

    that means objects need to have a __str__ function that renders a relevant
    path that can be used to access them.


    common element of all playlists is the path (or url)
    to access the records to play
    most simplified m3u is just a list of files
    """

    def __init__(self, items=[], item_type='path', prioritize=False,
                 source=None, sort_order=None, loop=False):

        self.source = source

        self.loop = loop
        self.prioritize = prioritize

        self.cur_pos = 0

        #probably storing paths only here (or names)
        #self.items = []
        #should be able to just use self now that is subclass of List

        #2008.12.10 08:48:56
        #using the items concept to store objects
        #actual python objects associated with the items
        #can be created upon request
        #self.objects = {}
        #self.object_type = object_type
        self.items = {}
        self.item_type = item_type

        for i in items:
            self.add_item(i)
            
        #can pass in "random" to keep random
        if sort_order:
            self.sort_order = sort_order
        else:
            self.sort_order = 'alpha'

    def add_item(self, i):
        #must be something else
        #index it's string representation
        #and hash the object for later retrieval
        if self.prioritize and (unicode(i) in self):
            self.remove(unicode(i))
            self.insert(0, unicode(i))
        else:
            if self.item_type == 'path':
                self.append(i)
            else:
                #include dupes
                self.append(unicode(i))
                self.items[unicode(i)] = i
        
    def sort_items(self, sort_order=None):
        if sort_order:
            self.sort_order = sort_order
            
        if self.sort_order == "alpha":
            self.sort()
        elif self.sort_order == "reverse":
            self.sort()
            self.reverse()
        else:
            #leave random
            pass

    def has_item(self, item):
        """
        very pose, but serves as a reminder if forgotten.
        """
        if item in self:
            return True
        else:
            return False

    def jump_to_num(self, number):
        """
        does not require that num be in range
        if it's not, don't return anything
        """
        #self.sort_items()
        if number < 0:
            self.cur_pos = 0
        elif number < len(self):
            self.cur_pos = number
        else:
            self.cur_pos = len(self)-1

        return self[self.cur_pos]

        
    def jump_to_item(self, item):
        if item in self:
            self.cur_pos = self.index(item)
        return self.cur_pos

    def get_next(self, item=None):
        #if we pass in an item, jump to that item's position
        if item:
            self.jump_to_item(item)

        if (self.cur_pos < len(self)-1):
            self.cur_pos += 1
            item = self[self.cur_pos]
            return item

        elif self.loop:
            self.cur_pos = 0
            item = self[self.cur_pos]
            return item

        else:
            #print "End of list!"
            return self[self.cur_pos]

    def get_prev(self, item=None):
        #self.sort_items()
        #if we pass in an item, jump to that item's position
        if item:
            self.jump_to_item(item)

        if self.cur_pos > 0:
            self.cur_pos -= 1
        elif self.loop:
            self.cur_pos = len(self)-1
        item = self[self.cur_pos]
        #self.play_item(item)
        return item


    def multi_filter(self, updates=path_updates):
        """
        go through a list of prefixes to filter
        """
        #clean up any quoted text... on local system we don't need it
        for item in self:
            index = self.index(item)
            self.remove(item)
            item = urllib.unquote(item)
            self.insert(index, item)
            
        for pu in updates:
            #debugging filter issues can be tricky:
            #print "replacing %s with %s" % (pu[0], pu[1])
            self.replace(pu[0], pu[1])
            #for i in self:
            #    print i
            
        #for diffing playlists and ignoring case, can do the following:
        ## for item in self:
        ##     index = self.index(item)
        ##     self.remove(item)
        ##     item = item.lower()
        ##     self.insert(index, item)
            
    def replace(self, pre, post):
        """
        scan all items in the list
        all instances of pre should be replaced with post

        # don't forget the following case with forward slashes:
        # search_string = "user\/setting\/password"
        # replace_string = "user/settings/password"

        """
        search_string = pre
        replace_string = post
        pattern = re.compile(search_string)
        for item in self:
            #os.path.normpath(item)
            if pattern.search(item):
                index = self.index(item)
                self.remove(item)
                #print "ORIGINAL ITEM: %s" % item
                item = pattern.sub(replace_string, item)
                #print "     NEW ITEM: %s" % item
                self.insert(index, item)

    #should be renamed to:
    #convert_from_relative
    #or
    #update_relative
    #or
    #relative_to_local
    #from implies from another format
    def from_relative(self):
        for item in self:
            index = self.index(item)
            self.remove(item)
            #get rid of leading slash... makes it look absolute
            #causes join to skip local_path
            if re.match('^\/', item):
                item = item[1:]
            item = str(make_node(item)) #os.path.join(local_path, item)
            print item
            self.insert(index, item)
            
    def from_file(self, filename=None):
        """ Default way to load a file """
        #if self.node and type(self.node) == "Directory":
        #    self = self.node.sounds
        #else:
        self.from_m3u(filename)

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
        ## new_entries = []
        ## for e in entries:
        ##     filtered_data = ''
        ##     for line in e.data.splitlines():
        ##         if line:
        ##             [ line ] = multi_filter( [line], updates)
        ##             #[ line ] = multi_filter( [line], path_updates)
        ##             if line:
        ##                 filtered_data += line + '\n'

        ##     e.data = filtered_data
        ##     new_entries.append(e)

        #make a new journal with normalized/filtered data
        j2 = Journal()
        j2.from_entries(entries)
        
        j2.filter_entries(updates)

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


    #2008.12.10 15:56:10
    #reenabling as_objects
    #now that MediaList is separate from osbrowser,
    #shouldn't be a bad thing to utilize it
    #and does make certain situations handy:
    def as_objects(self):
        #self.sort_items()
        olist = []
        for i in self:
            olist.append(self.get_object(i))
        return olist

    def get_object(self, path):
        """
        return a python osbrowser node like object for an item in the list
        """
        if not self.items.has_key(path):
            if self.item_type != "path":
                new_obj = make_node(path, self.item_type, relative=False)
            else:
                new_obj = make_node(path, relative=False)
                
            self.items[path] = new_obj
        return self.items[path]


    def flatten_and_sort(self):
        """
        generate a frequency list similar to the one in journals
        based on how many times an item shows up in the list
        then generate a new media list based on that frequency list
        """
        frequency = {}
        for i in self:
            if not frequency.has_key(i):
                frequency[i] = 1
            else:
                frequency[i] += 1

        items = []
        for key in frequency.keys():
            #if possible, should not re-order the items
            #if there is only one of them
            #keep them in the original order
            if key > 1:
                items.append( (frequency[key], key) )
        new_m = MediaList()
        items.sort()
        items.reverse()
        for i in items:
            new_m.add_item(i[1])

        #go through and get everything that was not weighted
        for i in self:
            if not i in new_m:
                new_m.add_item(i)
        
        return new_m

        


class XmlWriter(object):
    """
    XmlWriter and MediaList.to_xspf code adapted from m3u2xspf script:
    
    # Copyright (c) 2006, Matthias Friedrich <matt@mafr.de>
    #
    # This program is free software; you can redistribute it and/or modify
    # it under the terms of the GNU General Public License as published by
    # the Free Software Foundation; either version 2, or (at your option)
    # any later version.
    #
    # This program is distributed in the hope that it will be useful,
    # but WITHOUT ANY WARRANTY; without even the implied warranty of
    # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    # GNU General Public License for more details.
    """

    def __init__(self, outStream, indentAmount='  '):
            self._out = outStream
            self._indentAmount = indentAmount
            self._stack = [ ]

    def prolog(self, encoding='UTF-8', version='1.0'):
            pi = '<?xml version="%s" encoding="%s"?>' % (version, encoding)
            self._out.write(pi + '\n')

    def start(self, name, attrs={ }):
            indent = self._getIndention()
            self._stack.append(name)
            self._out.write(indent + self._makeTag(name, attrs) + '\n')

    def end(self):
            name = self._stack.pop()
            indent = self._getIndention()
            self._out.write('%s</%s>\n' % (indent, name))

    def elem(self, name, value, attrs={ }):
            # delete attributes with an unset value
            for (k, v) in attrs.items():
                    if v is None or v == '':
                            del attrs[k]

            if value is None or value == '':
                    if len(attrs) == 0:
                            return
                    self._out.write(self._getIndention())
                    self._out.write(self._makeTag(name, attrs, True) + '\n')
            else:
                    escValue = saxutils.escape(value or '')
                    self._out.write(self._getIndention())
                    self._out.write(self._makeTag(name, attrs))
                    self._out.write(escValue)
                    self._out.write('</%s>\n' % name)

    def _getIndention(self):
            return self._indentAmount * len(self._stack)

    def _makeTag(self, name, attrs={ }, close=False):
            ret = '<' + name

            for (k, v) in attrs.iteritems():
                    if v is not None:
                            v = saxutils.quoteattr(str(v))
                            ret += ' %s=%s' % (k, v)

            if close:
                    return ret + '/>'
            else:
                    return ret + '>'
