#!/usr/bin/env python
# ----------------------------------------------------------------------------
# moments
# Copyright (c) 2009-2010, Charles Brandt
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
# By: Charles Brandt [code at contextiskey dot com]
# On: *2010.12.01 11:08:25 
# License:  MIT

# Description:
originally part of scripts/launch.py

these functions help work with common higher level journal concepts

they should also be applicable to more than one script

for one off higher level functions, see the moments/scripts directory itself

"""

import re, os
from datetime import datetime

from journal import Journal
from timestamp import Timestamp, Timerange
from association import check_ignore, filter_list
from ascii import unaccented_map
from path import Path, load_journal

class ExtractConfig(object):
    """
    used in /c/charles/system/extract_config.py
    """
    def __init__(self):
        self.sources = ''
        self.ignores = ''
        self.extractions = []
        self.name = ''
        
## def extract_one(tags, path, extract_type):

##     these_tags = []
##     filename_tags = Path(path).to_tags()
##     these_tags.extend(filename_tags)
##     j = Journal()
##     j.from_file(path, add_tags=these_tags)
##     entries = j.extract(tags, extract_type)
##     #when it's time to save:
##     #j.to_file()
##     return entries

## def extract_tag(path, tag_string, extract_type='intersect'):
##     """
##     extract one tag from many files
    
##     for merging, see admin controller in pose
##     could be tricky with only one file to specify
##     might need to use command line for this for now

##     for each file in fpath
##     add any entry that matches tag_string criteria
##     to a local buffer
##     [local buffer will need to be a static (pre-configured) path
##      since we only have one variable path to work with,
##      and that needs to be the source
##      we can generate the output filename based on date and tags extracted
##      ]

##     and save original/source journal/log file without the extracted entries

##     very similar to Node->create_journal() or moments.journal.load_journal()
##     but we are doing a different action on each file (_extract_one)
##     so they need to stay separate
##     """

##     extracts = Journal()

##     tags = Tags().from_tag_string(tag_string)

##     add_tags = []
##     ignore_dirs = [ 'downloads', 'binaries' ]
##     log_check = re.compile('.*\.txt$')
##     if os.path.isdir(path):
##         for root,dirs,files in os.walk(path):
##             for f in files:
##                 if not log_check.search(f):
##                     continue
                
##                 cur_file = os.path.join(root, f)
##                 if not check_ignore(cur_file, ignore_dirs):
##                     entries = extract_one(tags, cur_file, extract_type)
##                     print "%s entries found in %s" % (len(entries), path)
##                     extracts.from_entries(entries)
                        
##     elif os.path.isfile(path) and log_check.search(path):
##         entries = extract_one(tags, path, extract_type)
##         print "%s entries found in %s" % (len(entries), path)
##         extracts.from_entries(entries)
##     else:
##         #no journal to create
##         pass

##     if len(extracts):
##         #now that we've extracted everything
##         #save the extracts journal to a log
##         t = datetime.now()
##         now = t.strftime("%Y%m%d%H%M%S")
##         fname = now + '-' + tag_string + '.txt'
##         #dest = os.path.join(config['log_local_path'], fname)
##         print "saving %s entries to %s" % (len(extracts), fname)
##         extracts.to_file(fname)

##         #could gather print statements to have something to return here:
##         #return output

##         return fname
##     else:
##         print "nothing extracted"

def extract_many(path, extractions, ignores=[], save=False, extract_type="intersect"):
    """
    rather than go through all files for every extraction
    it is nice to go through all extractions during each file

    save extractions for each file
    rather than accumulating until end

    will make it trickier for trial runs
    can print actions or make temp logs
    """
    these_tags = []
    filename_tags = Path(path).to_tags()
    #print filename_tags
    filename_tags = filter_list(filename_tags, ignores, search=True)
    #print filename_tags
    these_tags.extend(filename_tags)

    if not os.path.isfile(path):
        raise ValueError, "path must be a file, got: %s" % path
    j = Journal()
    
    #j.from_file(path, add_tags=these_tags)
    #can add tags to the export, but don't want to add them in here:
    has_entries = j.from_file(path)
    for (tags, destination) in extractions:
        entries = j.extract(tags, extract_type)
        if len(entries):
            print "found %s entries with tag: %s in: %s" % (len(entries), tags, path)
            entries.reverse()
            j2 = Journal()
            j2.from_file(destination)
            for e in entries:
                e.tags.extend(these_tags)
                j2.update_entry(e, 0)
                entry = e.render()
                e_ascii = entry.translate(unaccented_map()).encode("ascii", "ignore")
                print "adding entry to: %s\n%s" % (destination, e_ascii)
            if save:
                #this way we're saving any entries we extract to the new
                #destination before we save the original source file
                #
                #if there are permission problems writing the source file
                #at worst we'll have 2 copies of the same entry
                # (and that can be filtered out later)
                j2.to_file()

    # do *not* want to save if the file passed to the journal did not get parsed as having entries
    # this would result in a blank file being saved, resulting in data loss.
    # i.e. check both if save is desired ('save' variable)
    # and if journal had entries ('has_entries' variable)
    if save and has_entries:
        #when it's time to save:
        j.to_file()

def extract_tags(path, extractions=[], ignores=[], save=False,
                 extract_type='intersect'):
    """
    accept a list of extractions
    where each extraction consists of a set of tags to look for
    (using extract_type)
    and a destination where matching entries should be extracted to

    ignores is a list of tags to leave out of the found entries
    (good for filtering tags generated from the original file path)
    
    this duplicates the logic for scanning all files from extract_tag
    it feels more readable to separate the two

    *2009.08.29 13:20:46
    now part of the moments module itself

    not to be confused with the Journal.extract method
    these functions are higher level operations that utilize Journal.extract

    also:
    # take a list of tags,
    # and the directory or file that you want to use as the source of the tags
    # go through all files, and remove those tags
    # saving them in a new separate file (or specified existing file)

    # adapted from pose.controllers.tags.extract
    
    """
    
    add_tags = []
    ignore_dirs = [ 'downloads', 'binaries' ]
    log_check = re.compile('.*\.txt$')
    if os.path.isdir(path):
        for root,dirs,files in os.walk(path):
            for f in files:
                if not log_check.search(f):
                    continue
                
                cur_file = os.path.join(root, f)
                if not check_ignore(cur_file, ignore_dirs):
                    extract_many(cur_file, extractions, ignores, save,
                                 extract_type)
                        
    elif os.path.isfile(path) and log_check.search(path):
        extract_many(path, extractions, ignores, save, extract_type)
    else:
        #no logs to scan
        print "Unknown filetype sent as path: %s" % path

    #print "finished extracting multiple tags to multiple destinations"



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

    #print today_entries

    #CREATE TODAY'S LOG:
    today = os.path.join(destination, now.filename())
    #print today
    #print entries
    today_j = Journal()
    today_j.from_file(today)

    #print "Today journal length (pre): %s" % len(today_j)

    today_j.from_entries(today_entries)
    #for e in today_entries:
    #    today_j.update_entry(e, debug=True)
        
    if include_week:
        today_j.make_entry(flat, ['upcoming', 'this_week', 'delete'])

    print "Today journal length (post): %s" % len(today_j)

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

