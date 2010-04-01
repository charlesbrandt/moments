#!/usr/bin/env python
"""
#
# Description:
# uses moments to launch the last instances of files in use
# for text editing sessions.

# By: Charles Brandt [code at contextiskey dot com]
# On: *2009.09.28 15:12:44 
# License:  MIT
# Requires: moments

For development, see also:
/c/moments/moments/helpers.py
/c/moments/moments/launcher.py
/c/moments/instances.txt

Example call:

#!/bin/bash
python /c/moments/scripts/launch.py -i /c/instances.txt todo code now
echo "python /c/moments/moments/extract.py /c/other/todo.txt"
"""

import sys, os
from moments.launcher import launch, emacs
from moments.helpers import assemble_today, load_instance

#http://docs.python.org/library/optparse.html?highlight=optparse#module-optparse
from optparse import OptionParser

def now(files=[], destination="/c/outgoing", priorities="/c/priorities.txt", calendars="/c/calendars/"):
    today = assemble_today(calendars, destination, priorities)
    files.append(today)
    file_string = ' '.join(files)
    #print "Launcing Editor"

    #*2010.01.06 11:22:19 todo
    #make call to editor more generic
    #should not rely on emacs...
    #should be able to use any editor the user is comfortable with
    emacs(file_string)

def main():
    destination = "/c/outgoing"
    instances = "./instances.txt"
    motd = "/c/technical/motd.txt"
    calendars = "/c/calendars/"
    priorities = "/c/priorities.txt"

    parser = OptionParser()
    parser.add_option("-c", "--context", dest="context",
                      help="directory to look for all other files in")
    parser.add_option("-i", "--instance", "--instances", dest="instances",
                      help="pass in the instance file to look for instances in")
    parser.add_option("-m", "--motd", dest="motd",
                      help="pass in the file to look for motd in")
    (options, args) = parser.parse_args()
    if options.context:
        c = options.context
        instances = os.path.join(c, "instances.txt")
        calendars = os.path.join(c, "calendars")
        priorities = os.path.join(c, "priorities.txt")
        #motd = os.path.join(c, "motd.txt")
        #destination = os.path.join(c, "outgoing")
    else:
        if options.instances:
            instances = options.instances
        if options.motd:
            motd = options.motd

    # if nothing was passed in, start with some defaults
    if not len(args):
        #an instance is a textual list of file paths, one per line
        local_instance = None

        #if we don't have a file with instance entries in it,
        #we can create a temporary instance here:
        #local_instance = """ """

        if local_instance:
            #print "Loading the local instance: %s" % local_instance
            files = local_instance.splitlines()
            files = files[1:]
            #need option to generate and load now here too
            #rather than adding files to now 
            now(files, destination, priorities, calendars)
            
        elif local_instance is None:
            #go with defaults instances to load if nothing is passed in
            #it is ok to copy this file to multiple launch points,
            #and then set these as the defaults
            args = [ "now", "todo", "music", "system" ]
        
    #see if some args exist
    if len(args):
        # now serves as an example of what launch does for other instances:
        if "now" in args:
            #launch today's journal:
            
            #old way (breaks if now script is not in same path as launch):
            #from now import main
            #main()

            #today = assemble_today(calendars, destination, priority)

            try:
                files = load_instance(instances, "now")
            except:
                #even if there is no instance, it is still helpful to be able
                #to load the instance with today's log quickly.
                print "'now' instance not found in instances: %s" % instances
                print "additional files will not be loaded with daily log"
                print ""
                files = []
            now(files, destination, priorities, calendars)
            #now(files)
            
            #then remove now so it is not attempted later
            args.remove("now")
            #print "now should have been launched and removed from list."
            #print args

        #launch the rest
        #print args
        launch(args, instances)

    print ""
    f = open(motd)
    print f.read()
    f.close()
        
if __name__ == '__main__':
    #TODO: incorporate updating permissions as needed with this script.
    #print "sudo /c/update_permissions.sh"

    print "incase you need it: "
    print "/Applications/Emacs.app/Contents/MacOS/Emacs &"
    print ""

    # launch our instances
    main()

    #with open("/c/motd.txt") as f:
    #    print f.read()

    #reminder on how to extract finished, completed thoughts
    #(as long as they have been marked complete, M-x com)
    print "python /c/moments/moments/extract.py /c/todo.txt"
