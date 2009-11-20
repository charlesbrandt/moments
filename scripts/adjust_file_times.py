#!/usr/bin/env python
"""
Description:

Accept path(s) from the command line
then using preconfigured amount
adjust all files by the desired amount of time (forwards or backwards)

This can be helpful for devices that do no set the right file timestamps
(e.g. digital cameras)

By: Charles Brandt [code at contextiskey dot com]
On: *2009.11.19 10:34:42 
License:  MIT

Requires: moments

see also images_to_journal.py
and
split_by_day.py
"""
import sys, os
from moments.node import make_node
from moments.timestamp import Timestamp

def adjust(path):
    node = make_node(path)
    node_type = node.find_type()
    if node_type == "Directory":
        for f in node.files:
            modified = Timestamp()
            modified.from_epoch(f.mtime)
            print "Pre: %s" % modified

            #****configure your adjustment here****
            modified = modified.future(hours=1)
            #**************************************
            
            accessed = Timestamp()
            accessed.from_epoch(f.atime)
            f.change_stats(accessed, modified)
            modified = Timestamp()
            modified.from_epoch(f.mtime)
            print "Post: %s" % modified
            
    else:
        print node_type
        
def main():
    if len(sys.argv) > 1:
        helps = ['--help', 'help', '-h']
        for i in helps:
            if i in sys.argv:
                usage()
                exit()
        #skip the first argument (filename):
        for arg in sys.argv[1:]:
            files = adjust(arg)
                
if __name__ == '__main__':
    main()
