#!/usr/bin/env python
"""
#
# Description:
# takes one moment log and reverses the order of the entries
#
# useful to put oldest first (opposite of normal direction)

# By: Charles Brandt [code at contextiskey dot com]
# On: 2009.03.27 22:59:09 
# License:  MIT

# Requires: moments
*2009.10.02 22:51:26
renaming to sort log
should take a sort parameter
otherwise default to chronological (oldest first)
"""

import sys, os
from moments.journal import Journal
from moments.log import Log

def usage():
    print "python /c/moments/scripts/sort_log.py [source_log]"
    print "if destination supplied, will output there instead of temp.txt"
    print "python /c/moments/scripts/sort_log.py [source_log] [destination_log]"
    
def sort_log(f1, output="temp.txt", sort="chronological"):
    """
    'original'
    to keep the original order that the entries were added to the journal

    'reverse'

    'chronological' or 'oldest to newest'
    oldest entries first in the list

    'reverse-chronological'  or 'newest to oldest'
    if not all entries are wanted, see self.limit()
    
    """
    result = ''
    
    j = Journal()
    j.from_file(f1)

    l = Log(output)
    l.from_entries(j.sort_entries(sort=sort))
    l.to_file()
    l.close()

def main():
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            usage()
        f1 = sys.argv[1]
        if len(sys.argv) > 2:
            output = sys.argv[2]
        else:
            output = "temp.txt"
        sort_log(f1, output, sort='reverse-chronological')

    else:
        usage()
        
if __name__ == '__main__':
    main()
