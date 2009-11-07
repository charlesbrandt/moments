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
"""

import sys, os
from moments.journal import Journal
from moments.log import Log

def reverse_log(f1, f2="temp.txt"):
    """
    """
    result = ''
    
    j = Journal()
    j.from_file(f1)

    l = Log(f2)
    l.from_entries(j.sort_entries(sort="reverse"))
    l.to_file()
    l.close()
    
def main():
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            usage()
        f1 = sys.argv[1]
        if len(sys.argv) > 2:
            f2 = sys.argv[2]
        else:
            f2 = "temp.txt"
        reverse_log(f1, f2)
        
if __name__ == '__main__':
    main()
