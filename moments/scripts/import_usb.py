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

from moments.timestamp import Timestamp
from moments.path import Path
from split_by_day import split_by_day

def import_usb(src, dest_prefix):
    start = Timestamp()

    destinations = []

    destinations = split_by_day(src, dest_prefix)

    #if something goes wrong and you need to run this again:
    ## dirs = os.listdir(dest_prefix)
    ## if '.DS_Store' in dirs:
    ##     dirs.remove('.DS_Store')
    ## destinations = []
    ## for d in dirs:
    ##     destinations.append(os.path.join(dest_prefix, d))

    for dest in destinations:
        #run rotate, thumbnail generation
        print dest
        #d = make_node(dest)
        path = Path(dest)
        d = path.load()
        d.auto_rotate_images()
        #adjust times:
        #-2 hours
        #for multiple calls, may want to comment out
        #(i.e. if it has been run on the directory once already... )
        d.adjust_time(hours=-2)
        d.make_thumbs()
        #something is causing old timestamps to show up in the journal
        #trying to recreate directory object to fix
        d = path.load()
        #d = make_node(dest)
        d.scan_filetypes()
        d.files_to_journal(filetype="Image")
        d.files_to_journal(filetype="Sound")

    end = Timestamp()

    result = ''
    result += "From: %s To: %s,\n" % (str(start), str(end))
    if len(destinations):
        result += "Processed files from: %s to: %s\n" % (destinations[0], destinations[-1])
    else:
        result += "No files found\n"
    return result

def main():
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            usage()
        src = sys.argv[1]
        dest_prefix = sys.argv[2]
        result = import_usb(src, dest_prefix)
        print result
        
if __name__ == '__main__':
    main()
