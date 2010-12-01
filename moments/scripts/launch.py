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
/c/moments/moments/launcher.py
/c/moments/moments/helpers.py
/c/moments/moments/path.py
/c/moments/instances.txt

Example call:

#!/bin/bash
python /c/moments/scripts/launch.py -c /c/moments/ todo code now
echo "python /c/moments/moments/extract.py /c/other/todo.txt"
"""

import sys, os

from moments.launcher import edit_instance, edit
from moments.path import load_instance, Context
from moments.helpers import assemble_today

#http://docs.python.org/library/optparse.html?highlight=optparse#module-optparse
from optparse import OptionParser

def get_destination(destination=None):
    """
    set defaults for all operating systems here
    incase no destintation is explicitly specified.
    """
    if destination is None:
        if os.name == "nt":
            destination = r"C:\c\outgoing"
        else:
            destination = "/c/outgoing"
    return destination

def edit_today(context=None, instances=None, files=[], destination=None, priorities=None, calendars=None):
    if context and not instances:
        instances = context.instances
        
    files = []
    if instances and not files:
        try:
            files = load_instance(instances, "now")
        except:
            print "'now' instance not found in instances: %s" % instances
            print "additional files will not be loaded with daily log"
            print ""

    destination = get_destination(destination)
    if context:
        priorities = context.priorities
        calendars = context.calendars

    today = assemble_today(calendars, destination, priorities)
    files.append(today)
    file_string = ' '.join(files)

    #print "Launcing Editor"
    #specifying an editor here is optional... will default to configured
    #edit(file_string, editor="emacs")
    
    edit(file_string)

def launch(context='./', args=["now"], destination=None):
    """
    look in the supplied context for an instances file
    load the instances supplied as args
    open those instances as desired
    
    should be the python equivalent of calling the launch script from the command line
    somewhat simplified version of main since we don't need to deal with as many unknowns here
    """

    #sometimes might want to pass in just the context path and create Context object here
    string = "string"
    if type(string) == type(context):
        c = Context(context)
    else:
        #other times pass the actual context object in (created earlier)
        c = context
        
    if "now" in args:
        #now(c, files=files)
        edit_today(c, destination=destination)
        args.remove("now")

    print c.instances
    #launch the rest:
    edit_instance(args, c.instances)
    
    #*2010.11.05 17:25:10
    #I like the idea of motd
    #but it goes by so quick
    #especially when launching an editor
    #should probably be added to log

    ## if os.path.exists(motd):
    ##     f = open(motd)
    ##     message = f.read()
    ##     f.close()

    ##     if message:
    ##         print ""
    ##         print message

    ##     #with open(motd) as f:
    ##     #    print f.read()

def main():
    """
    command line equivalent of launch()
    """
    parser = OptionParser()
    parser.add_option("-c", "--context", dest="context",
                      help="directory to look for all other files in")
    parser.add_option("-i", "--instance", "--instances", dest="instances",
                      help="pass in the instance file to look for instances in")
    (options, args) = parser.parse_args()
    if options.context:
        context = Context(options.context)
    else:
        context = Context("./")
        
    #these will take precedence if specified separately:
    if options.instances:
        instances = options.instances
    else:
        instances = context.instances

    # if nothing was passed in, start with some reasonable defaults
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
            #edit_today(files, destination, priorities, calendars)
            edit_today(context, instances, files=files)
            
        elif local_instance is None:
            #go with defaults instances to load if nothing is passed in
            #it is ok to copy this file to multiple launch points,
            #and then set these as the defaults
            args = [ "now", "todo" ]
        
    launch(context, args, destination=None)

    ## #see if some args exist
    ## if len(args):
    ##     # now serves as an example of what launch does for other instances:
    ##     if "now" in args:
    ##         #launch today's journal:
            
    ##         #old way (breaks if now script is not in same path as launch):
    ##         #from now import main
    ##         #main()

    ##         #today = assemble_today(calendars, destination, priority)

    ##         edit_today(context, instances)
    ##         #edit_today(files, destination, priorities, calendars, instances)
    ##         #edit_today(files)
            
    ##         #then remove now so it is not attempted later
    ##         args.remove("now")
    ##         #print "now should have been launched and removed from list."
    ##         #print args

    ##     #launch the rest
    ##     #print args
    ##     edit_instance(args, instances)


        
if __name__ == '__main__':
    print "incase you need it: "
    print "/Applications/Emacs.app/Contents/MacOS/Emacs &"
    print ""

    # launch our instances
    main()

    #reminder on how to extract finished, completed thoughts
    #(as long as they have been marked complete, M-x com)
    print "python /c/moments/moments/extract.py /c/todo.txt"

    #TODO: incorporate updating permissions as needed with this script.
    #print "sudo /c/update_permissions.sh"

    print "sudo chmod -R 777 /c/outgoing"
    print ""
