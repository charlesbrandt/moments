#!/usr/bin/env python
"""
#
# Description:
# uses moments helper functions to
# launch the last instances in use for emacs sessions.

# By: Charles Brandt [code at contextiskey dot com]
# On: *2009.09.28 15:12:44 
# License:  MIT

# Requires: moments
"""

import sys, os
from moments.launcher import launch

def main():
    if len(sys.argv) > 1:
        helps = ['--help', 'help', '-h']
        for i in helps:
            if i in sys.argv:
                usage()
                exit()

    #skip the first argument (filename):
    args = sys.argv[1:]
    if not len(args):
        #go with defaults if nothing is passed in
        #(ok to copy this file to multiple launch points)
        args = [ "moments_documentation", "moments", "developer_todo",
                 "testing" ]
    launch(args)
        
if __name__ == '__main__':
    main()
    
    print ""
    # a reminder on how to extract finished, completed thoughts
    # (as long as they have been marked complete, M-x com)
    print "python /c/moments/moments/extract.py /c/todo.txt"

    #other things todo, commands in development
    #print "python /c/player/player.py"

    #recent runs:
    #*2009.11.17 19:20:54 
    #./launch.py moments_documentation moments developer_todo testing
