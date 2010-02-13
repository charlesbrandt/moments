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
/c/moments/scripts/split_by_day.py

$Id$ (???)
"""

import sys, os, subprocess, re
from moments.journal import Journal
from moments.association import check_ignore
from moments.tags import path_to_tags

def split_log(path, add_tags, destination='/c/'):
    print path
    j = Journal()
    j.from_file(path, add_tags=add_tags)
    if len(j):
        for e in j:
            #make sure they're all moments, otherwise we might want to look
            #at what is going on.
            assert e.created
            
        for e in j:
            dest_path = os.path.join(destination, str(e.created.year), str(e.created.month))
            dest = os.path.join(dest_path, e.created.filename())
            print dest
            #print e.render()

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
            e2 = existing.sort_entries('chronological')
            e2.to_file(dest)
            print "entries after: %s" % len(e2)

        print path
        raw_input('Ok to remove?')
        #get rid of the source to avoid confusion
        #rather than removing, remove from mercurial:
        command = "hg rm %s" % path
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        #os.remove(path)
        raw_input('Press Enter to continue...')

        print ""

def walk_logs(path, add_tags=[], subtract_tags=[],
              include_path_tags=True, create=False):
    """
    walk the given path and
    create a journal object for each log encountered in the path

    based on moments.journal.load_journal
    """
    #ignore_dirs = [ 'downloads', 'binaries' ]

    #this would be the place to add .hgignore items to the ignore_items list
    ignore_items = [ 'downloads', 'index.txt' ]
    log_check = re.compile('.*\.txt$')
    if os.path.isdir(path):
        for root,dirs,files in os.walk(path):
            for f in files:
                #make sure it at least is a log file (.txt):
                if not log_check.search(f):
                    continue

                if not check_ignore(os.path.join(root, f), ignore_items):
                    these_tags = add_tags[:]
                    if include_path_tags:
                        filename_tags = path_to_tags(os.path.join(root, f))
                        these_tags.extend(filename_tags)
                    #subtract tags last:
                    for tag in subtract_tags:
                        if tag in these_tags:
                            these_tags.remove(tag)
                    #j.from_file(os.path.join(root, f), add_tags=these_tags)
                    split_log(os.path.join(root, f), add_tags=these_tags)

    else:
        print "pass in a directory"


walk_logs('/path/to/logs', subtract_tags=['c'])
