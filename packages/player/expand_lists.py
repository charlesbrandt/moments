#!/usr/bin/env python
"""
# Description:

# parse a file with python video.py -sl [list] commands
# and expand the corresponding list to separate mplayer commands
# this will ensure that the marks are usable for systems that do not
# have video.py (or cannot use it)

# By: Charles Brandt [code at contextiskey dot com]
# On: *2009.05.01 01:24:26 
# License:  MIT

# Requires: 
"""
import sys,os,re

def expand_lists(f1):
    """
    # parse file
    # look for python video.py -sl [list] commands
    # and expand the corresponding list to separate mplayer commands
    
    """
    result = ''

    f = open(f1)
    for line in f.readlines():
        #go ahead and recreate the file
        result += line
        if re.search("-sl", line):
            #want to make sure we only split 4 times!
            parts = line.split(' ', 3)
            jumps = parts[2]
            cur_file = parts[3]
            for j in jumps.split(','):
                result += '-ss %s %s' % (j, cur_file)
    f.close()

    #reopen it for (over)writing
    f = open(f1, 'w')
    f.write(result)
    f.close()

def main():
    f1 = 'temp.txt'
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            usage()
        f1 = sys.argv[1]
        
    expand_lists(f1)
        
if __name__ == '__main__':
    main()
