#!/usr/bin/env python
"""
#
# Description:
# script to run through a supplied directory's moment logs
# (parse sub directories too) (similar to load journal)
# rather than loading into a large journal
# iterate over eacy file individually
# make a journal
# export entries based on day
# to a YYYY/MM/YYYYMMDD.txt structure

# By: Charles Brandt [code at contextiskey dot com]
# On: *2010.02.13 12:15:51 
# License:  MIT

# Requires: moments
#

see also:
/c/moments/moments/launcher.py
/c/moments/moments/journal.py
/c/moments/moments/timestamp.py
/c/moments/scripts/split_by_day.py

$Id$ (???)
"""

import sys, os, subprocess, re
from moments.journal import Journal
from moments.association import check_ignore
from moments.path import Path
from moments.timestamp import Timestamp

def split_log(path, add_tags, destination='/c/journal/'):
    print path
    j = Journal()
    j.from_file(path, add_tags=add_tags)
    if len(j):
        ## for e in j:
        ##     #make sure they're all moments, otherwise we might want to look
        ##     #at what is going on.
        ##     try:
        ##         assert e.created
        ##     except:
        ##         print e.render()
        ##         exit()
            
        for e in j:
            if hasattr(e, "created"):
                month = "%02d" % e.created.month
                dest_path = os.path.join(destination, str(e.created.year), month)
                dest = os.path.join(dest_path, e.created.filename())
                #print e.render()
            else:
                dest = os.path.join(destination, "no_date.txt")
            print dest

            existing = Journal()
            if not os.path.exists(dest):
                print "no log %s" % dest
                if not os.path.exists(dest_path):
                    print "missing directory: %s" % dest_path
                    os.makedirs(dest_path)
                existing.to_file(dest)
                
            existing.from_file(dest)
            print "entries before: %s" % len(existing)
            existing.update_entry(e)
            print "entries after update_entry: %s" % len(existing)
            e2 = existing.sort_entries('chronological')
            e2.to_file(dest)
            print "entries after: %s" % len(e2)

        print path
        raw_input('Ok to remove?')
        
        #get rid of the source to avoid confusion
        os.remove(path)
        #rather than removing, remove from mercurial:
        #command = "hg rm %s" % path
        #process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
        #                           stderr=subprocess.PIPE)

        raw_input('Press Enter to continue...')

        print ""

#def walk_logs(path, add_tags=["people"], subtract_tags=[],
def walk_logs(path, add_tags=[], subtract_tags=[],
              include_path_tags=True, create=False):
    """
    walk the given path and
    create a journal object for each log encountered in the path
    then split it up using split_logs function

    not recursive; only works on main directory

    based on moments.journal.load_journal
    """

    ignore_items = [ 'downloads', 'index.txt' ]
    log_check = re.compile('.*\.txt$')
    if os.path.isdir(path):
        for root,dirs,files in os.walk(path):
            for f in files:
                #make sure it is a log file (.txt):
                if not log_check.search(f):
                    continue

                if not check_ignore(os.path.join(root, f), ignore_items):
                    these_tags = add_tags[:]
                    if include_path_tags:
                        #*2010.12.01 22:26:16
                        #rather than include all tags from path
                        #check filename only
                        #if it is not a date tag, (e.g. boingboing.txt)
                        #then we can include those tags
                        #otherwise ok to skip
                        #filename_tags = path_to_tags(os.path.join(root, f))
                        #filename_tags = Path(os.path.join(root, f)).to_tags()
                        filename_tags = Path(os.path.join('/', f)).to_tags()
                        for t in filename_tags:
                            try:
                                ts = Timestamp(compact=t)
                            except:
                                #if it's *not* a valid timestamp,
                                #then we want to keep it as a tag
                                these_tags.append(t)

                        print "found tags: %s" % these_tags
                        #these_tags.extend(filename_tags)


                    #subtract tags last:
                    for tag in subtract_tags:
                        if tag in these_tags:
                            these_tags.remove(tag)
                    #j.from_file(os.path.join(root, f), add_tags=these_tags)
                    split_log(os.path.join(root, f), add_tags=these_tags)

    else:
        print "pass in a directory"


#walk_logs('/path/to/logs', subtract_tags=['c'])
#walk_logs('/c/incoming', subtract_tags=['c', 'incoming'])
walk_logs('/c/journal/incoming')
