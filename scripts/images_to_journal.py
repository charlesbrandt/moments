#!/usr/bin/env python
"""
*2009.08.09 04:02:25 
convert a directory of images into the corresponding journal for entries that reference the image file.

python images_to_journal.py [directory to scan]

take directory
open use osbrowser.meta.make_node(path)
scan_directory

*2009.10.18 21:36:25 todo
way to adjust time stamps on all files
or on all entries
closely related to:
/c/moments/scripts/images_to_journal.py 

*2009.10.21 15:27:06
could be generalized to generate a journal for any directory with files.

*2009.11.04 07:14:06
but in this case we wanted to filter all other content except images
"""
import sys#, os, subprocess
import moments
#from osbrowser.meta import make_node
from moments.node import make_node

def main():
    path = ''
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            usage()
        path = sys.argv[1]

    if not path:
        print "No path"
        exit()
        
    node = make_node(path, relative=False)
    node.scan_directory()
    node.scan_filetypes()
    #print node.images
    #app.sources = node.images
    j = moments.journal.Journal()

    for i in node.images:
        e = moments.moment.Moment()
        e.created = moments.timestamp.Timestamp(i.datetime())
        e.tags = [ 'image', 'capture', 'camera' ]
        e.data = i.path
        j.update_entry(e)

    print j
    #j.sort_entries("reverse-chronological")
    #l = Log(filename)
    #j.to_file('temp.txt')
    j.to_file('temp.txt', sort="reverse-chronological")

if __name__ == '__main__':
    main()
