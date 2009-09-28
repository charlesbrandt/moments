#!/usr/bin/env python
"""
#
# Description:
# take an iso file as parameter
# mount
# then play with a media player

# By: Charles Brandt [code at contextiskey dot com]
# On: *2009.07.30 13:01:17 
# License:  MIT

# Requires: moments

# TODO:
# adapt this to work on other operating systems
# can check what system we're on and then run

"""

import sys, os
from moments.journal import log_action
from launcher import mount_iso_macosx
    
def main():
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            usage()
        iso = sys.argv[1]
        print iso
        #mount_point = "/media/iso"
        #mount_iso(iso, mount_point)
        mount_iso_macosx(iso)
        log = "/c/media/movies/movies.txt"
        #log_action(log, iso, tags=['mount', 'play'])
        #totem(mount_point)
        #/Applications/DVD Player.app/Contents/MacOS/DVD Player
        print "emacs %s &" % log
        
if __name__ == '__main__':
    main()
