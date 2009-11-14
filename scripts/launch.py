#!/usr/bin/env python
"""
#
# Description:
adapted from moments now.py launcher
uses moments helper functions to launch the last instances in use for emacs sessions.

# By: Charles Brandt [code at contextiskey dot com]
# On: *2009.09.28 15:12:44 
# License:  MIT

# Requires: moments
"""

import sys, os
from moments.helpers import assemble_today, load_instance
from moments.launcher import emacs, terminal, nautilus

# now only
include_week = False
files = []
today = assemble_today("/c/personal/calendars/", "/c/outgoing", include_week)
files.append(today)
#can manually add files here
files.append("/c/personal/journal.txt")
file_string = ' '.join(files)
print emacs(file_string)

#or can call the customized now script
#from now import main
#main()

files = load_instance("/c/personal/instances.txt", "todo")
file_string = ' '.join(files)
print emacs(file_string)

#blank emacs for next group
#files = load_instance("/c/personal/instances.txt", "developer_todo")
#files = []
#file_string = ' '.join(files)
#print emacs(file_string)

# a reminder on how to extract finished, completed thoughts
# (as long as they have been marked complete, M-x com)
print "python /c/moments/moments/extract.py /c/personal/todo.txt"
