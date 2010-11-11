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
/c/moments/instances.txt

Example call:

#!/bin/bash
python /c/moments/scripts/launch.py -i /c/instances.txt todo code now
echo "python /c/moments/moments/extract.py /c/other/todo.txt"
"""

import sys, os
from datetime import datetime

from moments.launcher import edit_instance, edit
from moments.timestamp import Timestamp, Timerange
from moments.journal import Journal
from moments.path import load_journal, load_instance

#http://docs.python.org/library/optparse.html?highlight=optparse#module-optparse
from optparse import OptionParser

class Context(object):
    """
    A context is essentially just a collection of files with some standard attributes
    a place to collect files for a certain task, project, etc
    the main requirement is an instances file (typically instances.txt)
    
    see scripts/new_context.py

    todo:
    integrate new_context
    move this to moments (context.py)
    """
    def __init__(self, context):
        #context is just the parent directory
        self.context = context

        self.instances = os.path.join(context, "instances.txt")
        self.calendars = os.path.join(context, "calendars")
        self.priorities = os.path.join(context, "priorities.txt")
        self.motd = os.path.join(context, "motd.txt")
        
        #return [ self.instances, self.calendars, self.priorities, self.motd ]

## def check_context(context):
##     instances = "./instances.txt"
##     calendars = "/c/calendars/"
##     priorities = "/c/scripts/priorities.txt"
##     motd = "/c/scripts/motd.txt"

##     i = os.path.join(context, "instances.txt")
##     if os.path.exists(i):
##         instances = i
##     c = os.path.join(context, "calendars")
##     if os.path.exists(c):
##         calendars = c
##     p = os.path.join(context, "priorities.txt")
##     if os.path.exists(p):
##         priorities = p
##     m = os.path.join(context, "motd.txt")
##     if os.path.exists(m):
##         motd = m
##     #destination = os.path.join(context, "outgoing")

##     return [ instances, calendars, priorities, motd ]

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

def check_quotes(quotes_file):
    """
    similar to check_calendar, but looks in one file for the quote of the day
    """
    today_entries = []
    if os.path.exists(quotes_file):
        now = Timestamp()
        j = load_journal(quotes_file, add_tags=['quotes'])
        for e in j:
            #print "processing: %s" % e.render()
            #year may be in the past... update it to this year:
            try:
                #could be the case that Februrary has leap year days
                new_date = datetime(now.dt.year, e.created.month,
                                    e.created.day, e.created.hour,
                                    e.created.minute, e.created.second)
            except:
                new_date = None
            if new_date:
                new_stamp = Timestamp(new_date)
                new_data = e.render_data() + 'original date: %s' % e.created
                #j.make_entry(e.data, e.tags, new_stamp)
                j.make_entry(new_data, e.tags, new_stamp)

        # todo TODAY
        trange = now.compact(accuracy='day') + '-' + now.compact(accuracy='day') + '2359'
        #print trange
        (start, end) = Timerange(trange).as_tuple()
        today_entries = j.limit(start, end)
        #print today_entries

    return today_entries

def check_calendar(calendars, include_week=False):
    """
    check the files in calendars for entries that relate to today
    or this week if include week is True
    """
    today_entries = []
    if os.path.exists(calendars):
        now = Timestamp()

        #CALENDAR LOADING:
        this_month_file = '%02d.txt' % now.month
        this_month_path = os.path.join(calendars, this_month_file)
        j = load_journal(this_month_path, add_tags=['calendar'])
        #print len(j)
        # go ahead an convert recurring annual entries to this year
        # then if one is today, it should show up in the log
        annual_month_file = '%02d-annual.txt' % now.month
        annual_month_path = os.path.join(calendars, annual_month_file)
        annual = Journal()
        annual.from_file(annual_month_path, ['calendar', 'annual'])
        #print len(annual)
        #annual = load_journal(annual_month_path)
        for e in annual:
            #print "processing: %s" % e.render()
            #year may be in the past... update it to this year:
            try:
                #could be the case that Februrary has leap year days
                new_date = datetime(now.dt.year, e.created.month,
                                    e.created.day, e.created.hour,
                                    e.created.minute, e.created.second)
            except:
                new_date = None
            if new_date:
                new_stamp = Timestamp(new_date)
                new_data = e.render_data() + 'original date: %s' % e.created
                #j.make_entry(e.data, e.tags, new_stamp)
                j.make_entry(new_data, e.tags, new_stamp)

        flat = ''

        if include_week:
            #coming up this week (flatten them all, then the entry is ok to delete)
            trange = now.future(days=1).compact(accuracy='day') + '-' + now.future(weeks=1).compact(accuracy='day')
            #print trange
            (start, end) = Timerange(trange).as_tuple()
            upcoming_entries = j.limit(start, end)
            #print upcoming_entries

            #flatten upcoming:
            for e in upcoming_entries:
                flat += e.render_comment()
                flat += e.render_data()

        # todo TODAY
        trange = now.compact(accuracy='day') + '-' + now.compact(accuracy='day') + '2359'
        #print trange
        (start, end) = Timerange(trange).as_tuple()
        today_entries = j.limit(start, end)
        #print today_entries

    return today_entries

def assemble_today(calendars="/c/calendars", destination="/c/outgoing", priority="/c/priority.txt", include_week=False, quotes="/c/charles/golden_present.txt"):
    """ 
    look through all calendar items for events coming up
    today (at minumum) and
    this week (optionally)

    create a new log file for today and place any relevant events there
    return the name of the new file

    SUMMARY:
    helper function to assemble today's journal file from calendar items

    relies on filesystem structure for calendar
    expects calendar files to be in "calendars"
    and named either DD.txt or DD-annual.txt
    where DD is the two digit number representing the month (01-12)

    creates the new journal file in destination (default = /c/outgoing)
    """
    now = Timestamp()

    today_entries = check_calendar(calendars, include_week)
    today_entries.extend(check_quotes(quotes))

    #CREATE TODAY'S LOG:
    today = os.path.join(destination, now.filename())
    #print today
    #print entries
    today_j = Journal()
    today_j.from_file(today)

    today_j.from_entries(today_entries)
    if include_week:
        today_j.make_entry(flat, ['upcoming', 'this_week', 'delete'])
    today_j.to_file(today)

    #we only need to add the priority entry to today if this is the first time
    #other wise it may have changed, and we don't want to re-add the prior one
    if not today_j.tags.has_key('priority'):
        #add in priorities to today:
        priorities = load_journal(priority)
        entries = priorities.sort_entries(sort='reverse-chronological')
        if len(entries):
            #should be the newest entry
            e = entries[0]

            #check to see if yesterday's priority is the same as the most recent
            #entry in priorities.
            yesterday_stamp = now.past(days=1)
            yesterday = os.path.join(destination, yesterday_stamp.filename())
            yesterday_j = load_journal(yesterday)
            if yesterday_j.tags.has_key('priority'):
                yps = yesterday_j.tags['priority']
                print len(yps)
                #get the first one:
                p = yps[0]

                if p.data != e.data:
                    print "adding yesterday's priority to: %s" % priority
                    #think that putting this at the end is actually better...
                    #that way it's always there
                    #priorities.update_entry(p, position=0)
                    priorities.update_entry(p)
                    priorities.to_file(priority)
                    e = p

            j = load_journal(today)
            #should always have the same timestamp (in a given day)
            #so multiple calls don't create
            #mulitple entries with the same data
            #now = Timestamp()
            today_ts = Timestamp(compact=now.compact(accuracy="day"))
            j.make_entry(e.data, ['priority'], today_ts, position=None)
            j.to_file(today)
        else:
            print "No priorities found"
        print ""
        
    return today

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
