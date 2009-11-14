#!/usr/bin/env python
"""
#
# Description:
# take an iso file as parameter
# mount
# then play with a media player

# By: Charles Brandt [code at contextiskey dot com]
# On: *2009.07.07 20:38:33 
# License:  MIT

# Requires: moments

# TODO:
# adapt this to work on other operating systems
# can check what system we're on and then run

"""

import sys, os
from moments.journal import log_action
from moments.launcher import totem, mount_iso
    
def main():
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            usage()
        iso = sys.argv[1]
        print iso
        mount = "/media/iso"
        mount_iso(iso, mount)
        log = "/c/charles/movies/movies.txt"
        log_action(log, iso, tags=['mount', 'play'])
        totem(mount)
        print "emacs %s &" % log
        
if __name__ == '__main__':
    main()
