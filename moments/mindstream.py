#!/usr/bin/python -i
# ----------------------------------------------------------------------------
# moments
# Copyright (c) 2009-2010, Charles Brandt
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# ----------------------------------------------------------------------------
"""
# By: Charles Brandt <code at contextiskey dot com>
# On: 2010.12.02 10:41:22
# License:  MIT

# Description:

creating a search object with simplified API for common search operations
see search-orig.py for original version

should be able to run this with python interactive mode [search for notes]
to quickly find what is being looked for
and keep items loaded
for subsequent searches


Usage:
search.py /path/to/journal/to/load/

helpful to load this to interactive python mode (now default):
python -i search.py /c/technical/python/

old:
#!/usr/bin/env python

*2010.12.05 08:05:20
considering renaming this to Mindstream
very similar to a Journal object
but trying to keep it higher level.

A Journal and a Log are more closely related... collections of moments.
a Mindstream is more of a collection of Journals, even though those Journals will probably all get merged into one Journal object behind the scenes.

higher level operations that don't need to be included in a basic Journal object


not really just search... search is a hybrid space between the operating system level and pure python

mindstream should stay in pure python if possible.
"""

import sys, os
import re

from moments.journal import Journal
from moments.path import load_journal
from moments.timestamp import Timerange

class Timeline(object):
    """
    #2010.12.15 18:46:06
    also [2010.12.19 11:41:55] 
    combining with mindstream

    take a loaded journal (or journal subset)
    index based on various cycles

    allow easy formatting

    (do not worry about loading here)

    very similar to path.directory functionality
    and pose functionality
    """
    def __init__(self, journal, media='/c/binaries/journal'):
        """
        """
        self.j = journal

    def render_year(self, year=None):
        #if no year, use current year

        #look for all entries in this year

        #use the static image for the header
        #or, if no static, look for most popular image in this year

        #show all days for current month (summarize each day)

        #show highlights only for two previous months for current year (not current month)

        #show 3x3 grid of remaining months

        #show grid for previous years
        pass


class Mindstream(object):
    """
    """
    def __init__(self, source=None, look_for=[], debug=True):
        """
        load the journal path
        """
        #self.source = source

        #where we store what we've loaded
        self.j = Journal()

        #the list of items that have been loaded
        self.loaded = []

        if source:
            #self.j = load_journal(self.source)
            self.look_in(source)

        #if not using interactive mode
        if look_for:
            results = self.search_tags(look_for)
            for e in results:
                try:
                    print e.render()
                except:
                    print "non-ascii"

        if debug:
            print "Items loaded: %s" % len(self.j)

    def look_in(self, source):
        """
        wrapper for loading a journal
        """
        temp_j = load_journal(source)
        self.j.from_entries(temp_j)        
        self.loaded.append(source)
        
    def load_common(self, common_list="common.txt"):
        """
        common list is a simple list of paths
        with journals to load
        should be easy to edit
        then clear mind
        and reload for changes
        """
        #assuming cleared already if needed

        path = os.path.dirname(os.path.abspath( __file__ ))
        print path
        common_path = os.path.join(path, common_list)
        f = open(common_path)
        #this includes newlines:
        #lines = f.readlines()
        stuff = f.read()
        lines = stuff.splitlines()
        print lines
        for l in lines:
            self.look_in(l)
            
    def clear(self):
        """
        clear mind
        start fresh
        """
        del self.j
        self.j = []
        self.loaded = []
        #todo
        #way to see how much memory is consumed by current process?
        #should show before and after if so

    def entries_tagged(self, tags=[], temp_destination=None):
        """
        look for entries with the supplied tags
        assumes you already know the tags to look for 
        """
        #easy to forget to pass in a list of tags
        #when just looking for one tag
        if type(tags) != type([]):
            tags = [ tags ]
            
        found_entries = Journal()
        for t in tags:
            if self.j.tags.has_key(t):
                print len(self.j.tags[t])
                if temp_destination:
                    #save output to file
                    pass
                found_entries.from_entries(self.j.tags[t])

        found_entries = found_entries.sort_entries("reverse-chronological")
        return found_entries

    def lookup_tags(self, expression):
        """
        look in entry tags for matching expressions
        return a list of tags matching
        """
        tags = self.j.tags.keys()
        found = []
        for t in tags:
            if re.search(expression, t):
                found.append(t)
        return found


    def related_tags(self, tag):
        """
        find all of the other tags in entries that are tagged with 'tag'
        """
        #make sure we have it, otherwise nothing relates
        if not self.j.tags.has_key(tag):
            return []
        
        entries = self.j.tags[tag]
        related = []
        for e in entries:
            #todo:
            #could also generate a cloud
            #ranking most common related higher
            for t in e.tags:
                if t not in related:
                    related.append(t)


        return related

    def search_datas(self):
        """
        look in entry datas for matching expressions
        return a list of entries with matching datas
        """
        pass

    def extract_tags(self, tags, destination):
        """
        after saving the found entries to destination
        remove the found entries from the source files
        then reload our self.j
        """
        pass

    def time_range(self):
        """
        return a timerange object representing the total time covered
        with the currently loaded journal (no matter how it was loaded)
        """
        dates = self.j.dates.keys()
        dates.sort()
        start = dates[0]
        end = dates[-1]
        if start is None:
            start = dates[1]
        print start, end
        return Timerange(start=start, end=end)

def usage():
    print __doc__
    
def load():
    #requires that at least one argument is passed in to the script itself (sys.argv)
    if len(sys.argv) > 1:
        helps = ['--help', 'help', '-h']
        for i in helps:
            if i in sys.argv:
                usage()
                exit()

        look_in = sys.argv[1]
        
        if len(sys.argv) > 2:
            #could split tags if string
            look_for = [ sys.argv[2] ]
        else:
            look_for = [ ]

        print "Loading journal: %s" % look_in
        s = Mindstream(look_in, look_for)
        return s
    
    else:
        s = Mindstream()
        return s

        #usage()
        #exit()
        
if __name__ == '__main__':
    m = load()
    print "Welcome to moments searcher!"
    print "to see the document string, type:"
    print "print __doc__"
    #print "for usage notes, call usage()"
    print "search object bound to 's' variable"
    print "dir(s) for details"

    def look_in(*args, **kwargs):
        #wrapping for simplicity
        #todo:
        #way to do this automatically?
        #is that needed?
        global s
        s.look_in(*args, **kwargs)
