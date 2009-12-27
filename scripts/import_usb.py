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

from moments.timestamp import Timestamp

def main():
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            usage()
        src = sys.argv[1]
        dest_prefix = sys.argv[2]

        start = Timestamp()
        destinations = split_by_day(src, dest_prefix)

        for dest in destinations:
            #run rotate, thumbnail generation
            print dest
            d = make_node(dest)
            d.auto_rotate_images()
            #adjust times:
            #-2 hours
            #for multiple calls, may want to comment out
            #(i.e. if it has been run on the directory once already... )
            d.adjust_time(hours=-2)
            d.make_thumbs()
            #something is causing old timestamps to show up in the journal
            #trying to recreate directory object to fix
            d = make_node(dest)
            d.scan_filetypes()
            d.files_to_journal(filetype="Image")
            d.files_to_journal(filetype="Sound")

        end = Timestamp()
        print "From: %s To: %s," % (str(start), str(end))
        if len(destinations):
            print "Processed files from: %s to: %s" % (destinations[0], destinations[-1])
        else:
            print "No files found"
              
        
if __name__ == '__main__':
    main()
