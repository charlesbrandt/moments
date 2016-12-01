#!/usr/bin/env python
"""
# By: Charles Brandt <code at contextiskey dot com>
# On: 2015.01.12 18:42:54
# License:  MIT

# Description:

"""

import sys, os, codecs

#class SortableListMetaData(object):
#class SortableListFormat(object):
class SortableListSettings(object):
    """
    store any details that are related to a list here
    don't want to make the list any more complex
    but it will be important to keep track of:

    what is on the list
    e.g.
    song, " - ", artist, " - ", other

    or

    path

    and also what collection(s) (or drive dirs)
    to look in for corresponding content
    """
    def __init__(self, arg=None):
        """
        """
        #print "object passed: %s from command line" % arg

        self.format = ""

        #where to look for the corresponding details for items on the list:
        #self.collections = ""
        self.sources = ""
        
class SortableTextList(list):
    """
    may be close to a medley.collector.Cluster object too
    (but every item is separated by a new line, instead of a space)
    """
    #this is the way Cluster orders parameters...
    #wondering if it is more common to pass a list in as default on init
    #def __init__(self, source=None, ordered_list=[]):
    
    def __init__(self, ordered_list=[], source=None):
        self.extend(ordered_list)
        self.source = source
        if self.source:
            self.load()
        
    def load(self, source):
        """
        """
        if source is None:
            source = self.source
        else:
            self.source = source

        if not source:
            raise ValueError, "No source specified: %s" % source
                
        #this is a very simple loading process
        #that only loads a simple text list
        src_file = codecs.open(source, 'r', encoding='utf-8', errors='ignore')
        lines = src_file.readlines()

        for line in lines:
            self.append(line.strip())

    def save(self, destination=None):
        """
        """
        if destination is None:
            destination = self.source

        #otherwise, if a new destination is sent, save it as the new source
        #that way subsequent saves won't need to specify it
        else:
            self.source = destination

        if not destination:
            raise ValueError, "No destination specified: %s" % destination
        
        dst_file = codecs.open(destination, 'w', encoding='utf-8', errors='ignore')
        for line in self:
            dst_file.write(line + '\n')
            #dst_file.write(line)
        
        dst_file.close()

    def render(self, format='text'):
        """
        look at settings to determine source and lookup pattern
        then, 
        for each item in list
        look it up in corresponding collection and call render on that
        """
        result = ''
        for item in self:
            if callable(hasattr(item, "render")):
                result += item.render()
            else:
                result += str(item)
                
        return result

    def move_item_at(self, source, destination):
        """
        take item at source position
        move it to destination position
        """
        item = self.pop(source)
        self.insert(destination, item)

    def move(self, name, destination):
        """
        find the position of the name
        move that to the destination
        """
        source = self.index(name)
        self.move_item_at(source, destination)

    def bump(self, name):
        """
        move the named item to the top of the list
        """
        self.move(name, 0)
    
class SortableList(SortableTextList):
    """
    Instead of only containing text items
    this could eventually allow objects

    (currently still text [2016.12.01])
    """
    #this is the way Cluster orders parameters...
    #wondering if it is more common to pass a list in as default on init
    #def __init__(self, source=None, ordered_list=[]):
    
    def __init__(self, ordered_list=[], source=None):
        self.extend(ordered_list)
        self.source = source
        if self.source:
            self.load()
        
    def load(self, source):
        """
        """
        if source is None:
            source = self.source
        else:
            self.source = source

        if not source:
            raise ValueError, "No source specified: %s" % source
                
        #TODO:
        #look for corresponding settings file
        #filename + '-settings.json' ?
        #load settings
        #store settings as self.settings

        #TODO:
        # if settings, could parse source accordingly

        #TODO:
        # consider an import or export
        # to assist with more complex sources / destinations...
        # should still be able to distill
        # the imported option down to a simple text list

        #this is a very simple loading process
        #that only loads a simple text list
        src_file = codecs.open(source, 'r', encoding='utf-8', errors='ignore')
        lines = src_file.readlines()

        for line in lines:
            self.append(line.strip())


def usage():
    print __doc__
    
def main():
    #requires that at least one argument is passed in to the script itself (sys.argv)
    if len(sys.argv) > 1:
        helps = ['--help', 'help', '-h']
        for i in helps:
            if i in sys.argv:
                usage()
                exit()

        #skip the first argument (filename):
        for arg in sys.argv[1:]:
            a = Sortable_list(arg)

    else:
        #a = Sortable_list()
        usage()
        exit()
        
if __name__ == '__main__':
    main()
