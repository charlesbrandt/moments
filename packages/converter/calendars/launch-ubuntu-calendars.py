#!/usr/bin/env python
"""
#
# Description:
# start up calendaring 

# By: Charles Brandt [code at contextiskey dot com]
# On: *2009.07.13 06:51:34 
# License:  MIT

# Requires: moments

# TODO:
# adapt this to work on other operating systems
# can check what system we're on and then run

"""

import sys, os, subprocess
from datetime import datetime
from moments.journal import log_action
from launcher import terminal, emacs, nautilus, evolution

def main():
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            usage()
        iso = sys.argv[1]
        print iso

    result = ''

    result += nautilus("/c/media/calendars")
    result += terminal(["/c/media/calendars"])

    now = datetime.now()
    month = now.strftime("%m")
    result += emacs("/c/media/calendars/%s.txt" % month)
    result += emacs("/c/media/calendars/%s-annual.txt" % month)
    result += evolution()
    print result
    print "See also:"
    print "/c/media/projects/calendar-todo.txt"

    
if __name__ == '__main__':
    main()
