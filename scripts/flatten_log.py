#!/usr/bin/env python
"""
#
# Description:
# takes one moment log and removes all timestamps (and tags???)

# By: Charles Brandt [code at contextiskey dot com]
# On: 2009.03.25 08:22:07 
# License:  MIT

# Requires: moments
"""

import sys, os
from moments.journal import Journal
#from moments.timestamp import Timestamp

def flatten_log(f1, f2="temp.txt"):
    """
    """
    result = ''
    
    j = Journal()
    j.from_file(f1)
    j.flatten(f2)
    
def main():
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            usage()
        f1 = sys.argv[1]
        f2 = sys.argv[2]
        flatten_log(f1, f2)
        
if __name__ == '__main__':
    main()
