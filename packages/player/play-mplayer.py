#!/usr/bin/env python
"""
#
# Description:

# takes two moment logs and merges them

# By: Charles Brandt [code at contextiskey dot com]
# On: 2009.01.29 18:15:01 
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
import sys, os, subprocess
from moments.journal import Journal
from osbrowser import meta
from medialist.medialist import MediaList
import time
import re

#       -ss <time> (also see -sb)
#              Seek to given time position.

#              EXAMPLE:
#                 -ss 56
#                      Seeks to 56 seconds.
#                 -ss 01:10:00
#                      Seeks to 1 hour 10 min.

def play_one(command):

    #f = meta.make_node(relative_path)
    #f.log_action(["watch", "movie"])
    #cmd = 'mplayer -softvol -vo xv -loop 0 %s' % f.path
    cmd = 'mplayer -softvol -vo xv -loop 0 %s' % command
    print cmd
    pipe = subprocess.Popen(cmd, shell=True)    
    time.sleep(2)

def play_list(f1):
    m = MediaList()
    m.from_file(f1)
    #m.from_relative()
    for i in m:
        if re.match("^\*", i):
            print "comment: %s" % i
        elif i:
            print "seek found"
            play_one(i)
    print "**********ALL DONE****************"
        
def add_quotes(f1):
    m = MediaList()
    m.from_file(f1)
    #m.from_relative()
    for i in m:
        i = '"%s"' % i
        print i
        
def main():
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            usage()
        f1 = sys.argv[1]
        #f2 = sys.argv[2]
        play_list(f1)
        #add_quotes(f1)
        
if __name__ == '__main__':
    main()
