#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# moments
# Copyright (c) 2009-2017, Charles Brandt
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# ----------------------------------------------------------------------------
"""
# Description:
# a collection of functions to assist with launching applications

# By: Charles Brandt [code at contextiskey dot com]
# On: *2009.07.10 11:54:55
# License:  MIT

# TODO:
# adapt this to work on other operating systems
# can check what system we're on and then run

make this callable
add a main function
pass the launch to call via command line
(maybe someday a running process like quicksilver/gnome-do)
"""
from __future__ import print_function
from __future__ import absolute_import
from builtins import range
from builtins import object
import os, sys, subprocess

#__package__ = 'launch'

#from moments.path import load_journal, load_instance, Context, Path
#from moments.path import load_journal, load_instance, Path
#from moments.timestamp import Timestamp
#from moments.journal import Journal

#from moments.path import load_journal, load_instance, Path
from sortable.path import load_journal, load_instance, Path
from moments.timestamp import Timestamp
from moments.journal import Journal

#http://docs.python.org/library/optparse.html?highlight=optparse#module-optparse
from optparse import OptionParser

def simple_launcher(command):
    """
    more of an example / template for other scripts to use
    often look here to remember how subprocess works
    building a command is left to the caller (example commented out)
    """
    ## arg_string = ''
    ## for wd in working_dirs:
    ##     arg_string += ' --tab --working-directory=%s' % wd
    ## for i in range(tabs):
    ##     args += ' --tab'

    #command = "gnome-terminal %s &" % args


    process = subprocess.Popen(command, shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

    #varying degrees of success with these
    #process.communicate()[0]
    #process.communicate()
    #process.wait()

    while process.poll() is None:
        #depending on which channel has output, can tailor that here
        l = process.stderr.readline()
        #l = process.stdout.readline()
        print(l)

    #when process terminates, can finish printing the rest:
    print(process.stdout.read())

    return command + "\n"


############################################################
# generic launchers
############################################################

#will accept more than one instance
def edit_instance(args, instance='/c/instances.txt', editor="emacs"):
    for arg in args:
        #try:
        files = load_instance(instance, arg)
        file_string = ' '.join(files)
        edit(file_string, editor=editor)
        #echo(file_string)
        print("Loading: %s" % arg)
        #except:
        #    print "Could not load instance: %s" % arg

#feel free to set the editor to any preferred default here
#this should be the call to make any time an editor is needed
def edit(source='', editor="emacs"):
    if editor == "emacs":
        emacs(source)
    else:
        print("Unknown editor: %s" % editor)

def browse(urls=[], browser="firefox"):
    """
    launch a web browser
    """
    if browser == "firefox":
        firefox(urls)
    else:
        print("Unknown broswer: %s" % browser)

def play(source='', start=0):
    """
    source should be either a path or a string
    if it's just a string, then should try to identify the correct path to the media
    (search a library of local data?)
    """
    process = None
    p = Path(source)
    if not p.exists():
        #TODO
        #could search here
        #but for now...
        print("Could not find: %s" % source)
    else:
        process = vlc(source, start)
    return process

def watch(source=''):
    pass

def movie(source=''):
    pass

def picture(source=''):
    pass

#system_explorer, computer, etc
def file_browse(source=''):
    if sys.platform == "linux2":
        if check_which('nautilus'):
            nautilus(source)
        elif check_which('exo-open'):
            file_manager(source)

    elif sys.platform == "darwin":
        print("launch finder here")
    else:
        print("launch explorer here")

def terminal(working_dirs=[], tabs=0):
    """
    todo:
    this should be more operating system agnostic
    """
    args = ''
    for wd in working_dirs:
        args += ' --tab --working-directory=%s' % wd
    for i in range(tabs):
        args += ' --tab'

    command = "gnome-terminal %s &" % args
    #would be better to launch this as a background process and exit the script
    #process = subprocess.Popen(command)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    #process.communicate()[0]
    return command + "\n"

def check_which(item=''):
    """
    check if a command exists on unix systems with which
    """
    command = "which %s" % (item)
    process = subprocess.Popen(command, shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

    while process.poll() is None:
        #depending on which channel has output, can tailor that here
        l = process.stderr.readline()
        #l = process.stdout.readline()
        print(l)

    result = process.stdout.read()
    #if result has something, it exists
    #works as a binary test
    return result


############################################################
#application specific launchers
############################################################

def nautilus(source=''):
    command = "nautilus %s &" % source
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    return command + "\n"

def file_manager(source=''):
    """
    filemanager is the default file browser available on xubuntu

    for OS agnostic version, see file_browse()
    """
    command = "exo-open --launch FileManager %s &" % source
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    return command + "\n"



def rsync(source, destination, verbose=True):
    command = "rsync -av %s %s" % (source, destination)
    if verbose:
        print(command)

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    output = process.communicate()[0]
    if output:
        print(output)
    #this stalls for rsync...
    #process.wait()

def emacs(source=''):
    #print os.name
    #print sys.platform
    if sys.platform == "darwin":
        #command = "/Applications/Emacs.app/Contents/MacOS/Emacs %s -f delete-other-windows &" % source
        command = "/Applications/Emacs.app/Contents/MacOS/Emacs %s &" % source
    else:
        #command = "emacs %s -f delete-other-windows &" % source
        command = "emacs %s &" % source
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    #process.communicate()[0]
    return command + "\n"


def echo(source=''):
    """
    using this to attempt to find source of:
    Exception exceptions.TypeError: TypeError("'NoneType' object is not callable",) in <bound method Popen.__del__ of <subprocess.Popen object at 0xffa5d0>> ignored
    seems to only occur with shell=True
    """
    #print os.name
    #print sys.platform
    command = "echo %s" % source
    #process = subprocess.Popen(command, shell=True)
    #process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
    #                           stderr=subprocess.PIPE)
    #process = subprocess.check_call([command], {'shell':True})
    process = subprocess.check_call([command])
    #process.communicate()[0]
    return command + "\n"

def vlc(source='', start=0):
    #command = "vlc --play-and-exit --start-time %s %s &" % (start, source)
    command = "vlc --start-time %s %s" % (start, source)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    #return command + "\n"
    return process

def totem(movie):
    command = "totem --fullscreen %s" % (movie)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    return command + "\n"

def evolution(component="calendar"):
    #-c, --component=COMPONENT
    #    Start Evolution by activating the desired component.   COMPONENT
    #    is one of 'mail', 'calendar', 'contacts', 'tasks', 'memos'.
    command = "evolution --component=%s" % (component)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    return command + "\n"

def mount_iso(source, mount):
    if not os.path.exists(mount):
        print("creating mount point: %s" % mount)
        os.mkdir(mount)

    #try unmounting first
    command = "sudo umount %s" % (mount)
    print("To unmount:")
    print(command)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    output = process.communicate()[0]
    if output:
        print(output)


    command = "sudo mount %s %s -t iso9660 -o loop" % (source, mount)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    output = process.communicate()[0]
    if output:
        print(output)

def mount_iso_macosx(source):
    #http://osxdaily.com/2008/04/22/easily-mount-an-iso-in-mac-os-x/
    command = "sudo hdiutil mount %s" % (source)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    output = process.communicate()[0]
    if output:
        print(output)

def dvd_macosx(movie):
    command = r"/Applications/DVD\ Player.app/Contents/MacOS/DVD\ Player &"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    return command + "\n"

def firefox(url=None, urls=[]):
    """
    firefox(urls=[ "http://google.com", "http://news.google.com"])

    be sure to pass urls in with the http:// prefix

    i.e.
    "http://www.google.com" is good
    "google.com" is not good

    http://stackoverflow.com/questions/832331/launch-a-webpage-on-a-firefox-win-tab-using-python
    Thanks Nadia!

    http://docs.python.org/library/webbrowser.html

    firefoxes "Preferences->Tab" seem to override anything done here

    *2011.08.31 08:29:51
    for more advanced browser control, see Selenium and Webdriver
    examples available as site scrape code

    """
    import webbrowser
    #print url
    if url is not None:
        webbrowser.open_new(url)
    elif urls:
        url = urls.pop(0)
        #webbrowser.open(url, new=1)
        webbrowser.open_new(url)
        for u in urls:
            webbrowser.open_new_tab(u)

#############################################
# main context launching functionality
#############################################

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
        string = ''
        if type(context) == type(string):
            #context is just the parent directory
            self.context = context

            self.instances = os.path.join(context, "instances.txt")
            self.calendars = os.path.join(context, "calendars")
            self.priorities = os.path.join(context, "priorities.txt")
            self.motd = os.path.join(context, "motd.txt")

        else:
            #going to assume that if it's not a string, it's already one of us:
            self = context


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

#following originally in launch.py
#seems more related to watch
def assemble_today(calendars="/c/calendars", destination="/c/outgoing", priority="/c/priority.txt", include_week=False, quotes="/c/yoga/golden_present.txt"):
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

    #*2011.09.02 18:55:24
    #not sure where these functions went...
    #they should be in the launch module
    #today_entries = check_calendar(calendars, include_week)
    #today_entries.extend(check_quotes(quotes))
    today_entries = []

    #print today_entries

    #CREATE TODAY'S LOG:
    today = os.path.join(destination, now.filename())
    #print today
    #print entries
    today_j = Journal()
    today_j.load(today)

    #print "Today journal length (pre): %s" % len(today_j.entries())

    today_j.update_many(today_entries)
    #for e in today_entries:
    #    today_j.update_entry(e, debug=True)

    if include_week:
        today_j.make(flat, ['upcoming', 'this_week', 'delete'])

    print("Today journal length (post): %s" % len(today_j.entries()))

    today_j.save(today)

    #we only need to add the priority entry to today if this is the first time
    #other wise it may have changed, and we don't want to re-add the prior one
    if 'priority' not in today_j._tags:
        #add in priorities to today:
        priorities = load_journal(priority)
        entries = priorities.sort('reverse-chronological')
        if len(entries):
            #should be the newest entry
            e = entries[0]

            #check to see if yesterday's priority is the same as the most recent
            #entry in priorities.
            yesterday_stamp = now.past(days=1)
            yesterday = os.path.join(destination, yesterday_stamp.filename())
            yesterday_j = load_journal(yesterday)
            if 'priority' in yesterday_j._tags:
                yps = yesterday_j._tags['priority']
                print(len(yps))
                #get the first one:
                p = yps[0]

                if p.data != e.data:
                    print("adding yesterday's priority to: %s" % priority)
                    #think that putting this at the end is actually better...
                    #that way it's always there
                    #priorities.update_entry(p, position=0)
                    priorities.update(p)
                    priorities.save(priority)
                    e = p

            j = load_journal(today)
            #should always have the same timestamp (in a given day)
            #so multiple calls don't create
            #mulitple entries with the same data
            #now = Timestamp()
            today_ts = Timestamp(compact=now.compact(accuracy="day"))
            j.make(e.data, ['priority'], today_ts, position=None)
            j.save(today)
        else:
            print("No priorities found")
        print("")

    return today

def edit_today(context=None, instances=None, files=[], destination=None, priorities=None, calendars=None):
    if context and not instances:
        instances = context.instances

    files = []
    if instances and not files:
        try:
            files = load_instance(instances, "now")
        except:
            print("'now' instance not found in instances: %s" % instances)
            print("additional files will not be loaded with daily log")
            print("")

    #set defaults for all operating systems here
    #incase no destintation was explicitly specified.
    if destination is None:
        if os.name == "nt":
            #destination = r"C:\c\outgoing"
            destination = r"C:\c\out"
        else:
            #destination = "/c/outgoing"
            destination = "/c/out"

    if not os.path.exists(destination):
        os.makedirs(destination)

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

def edit_journal(destination=None):
    if destination is None:
        if os.name == "nt":
            #destination = r"C:\c\outgoing"
            destination = r"C:\c\out"
        else:
            #destination = "/c/outgoing"
            destination = "/c/out"

    if not os.path.exists(destination):
        os.makedirs(destination)

    files = []
    today = os.path.join(destination, 'journal.txt')
    files.append(today)
    file_string = ' '.join(files)

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
    #string = "string"
    #if type(string) == type(context):
    if isinstance(context, str) or isinstance(context, str):
        c = Context(context)
    elif isinstance(context, Context):
        #other times pass the actual context object in (created earlier)
        c = context
    else:
        raise ValueError("Unknown type: %s for context: %s" % (type(context), context))

    if "now" in args:
        #now(c, files=files)
        edit_today(c, destination=destination)
        args.remove("now")

    elif "journal" in args:
        #now(c, files=files)
        edit_journal(destination=destination)
        args.remove("journal")

    print(c.instances)
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

if __name__ == '__main__':
    """
    command line interface to launch()
    """
    print("incase you need it: ")
    print("/Applications/Emacs.app/Contents/MacOS/Emacs &")
    print("")

    # launch our instances
    parser = OptionParser()
    parser.add_option("-c", "--context", dest="context",
                      help="directory to look for all other files in")

    #default is to load the instance,
    #but this can specify a non-standard location for instances
    #(not instances.txt, which is the default)
    parser.add_option("-i", "--instance", "--instances", dest="instances",
                      help="pass in the instance file to look for instances in")

    #TODO
    #*2016.02.23 18:17:09
    # haven't changed this in a long time!
    #way to specify if launch should try to load a whole workspace
    parser.add_option("-w", "--workspace", "--workspaces", dest="workspaces",
                      help="flag to check for workspaces, expects context")
    parser.add_option("-s", "--session", "--sessions", dest="sessions",
                      help="flag to check for sessions, expects context")


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
        #these are often stored in instances.txt files in a context
        #if we don't have a file with instance entries in it,
        #we can create a temporary instance here:
        local_instance = ""

        if local_instance:
            print("Loading the local instance: %s" % local_instance)
            files = local_instance.splitlines()
            files = files[1:]
            #need option to generate and load now here too
            #rather than adding files to now
            #edit_today(files, destination, priorities, calendars)
            edit_today(context, instances, files=files)

        else:
            #go with defaults instances to load if nothing is passed in
            #args = [ "now", "todo" ]
            args = [ "journal" ]

    print("launching: %s with args: %s" % (context.context, args))
    launch(context, args, destination=None)

    #reminder on how to extract finished, completed thoughts
    #(as long as they have been marked complete, M-x com)
    #print "python /c/mindstream/scripts/extract.py /c/todo.txt"

    #this reminder should go in any launch.sh scripts at the end, as needed:
    #print "sudo chmod -R 777 /c/outgoing"
    #print ""
