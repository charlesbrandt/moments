#!/usr/bin/env python
"""
#
# Description:

# takes a list of m3u files
# creates a media list out of all of them
# sorts the most frequent ones to show up first

# By: Charles Brandt [code at contextiskey dot com]
# On: 2009.03.22 13:24:03 
# License:  MIT

# Requires:  medialist


$Id$ (???)
"""
import sys
from medialist.medialist import MediaList

def order_media(files, ofile="temp.txt"):
    result = ''
    
    m = MediaList()

    for f in files:
        m.from_m3u(f)

    new_m = m.flatten_and_sort()

    result += "SAVING as: %s\n" % ofile
    new_m.to_file(ofile)
        
    print result
    
def main():
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            usage()
        files = sys.argv[1:]
        order_media(files)
        
if __name__ == '__main__':
    main()
