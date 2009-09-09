#!/usr/bin/env python
"""
#
# Description:

# convert minutes and seconds string to just seconds

# By: Charles Brandt [code at contextiskey dot com]
# On: *2009.02.24 19:17:25 
# License:  MIT

# Requires: moments
#
# Sources:
#
# Thanks:
#
# TODO:


$Id$ (???)
"""
import sys
def main():
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            usage()
        time = sys.argv[1]
        seconds = int(time[-2:])
        minutes = int(time[:-2])
        print minutes*60+seconds
        
if __name__ == '__main__':
    main()
