#!/usr/bin/env python
"""
#
# Description:
# copy media from the USB device to the local filesystem (long term storage)

# By: Charles Brandt [code at contextiskey dot com]
# On: *2009.08.05 14:08:04 
# License:  MIT

# Requires: moments, osbrowser

# originally created in Pose
python /c/code/python/scripts/import_usb.py [source_dir] [destinatin_dir]

"""

import sys, os, subprocess
from moments.node import make_node
from split_by_day import split_by_day

def main():
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            usage()
        src = sys.argv[1]
        dest_prefix = sys.argv[2]
        
        destinations = split_by_day(src, dest_prefix)

        for dest in destinations:
            #run rotate, thumbnail generation
            print dest
            d = make_node(dest)
            d.auto_rotate_images()
            d.make_thumbs()

        
if __name__ == '__main__':
    main()
