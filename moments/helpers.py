"""
*2009.09.28 12:01:59
helper functions for use with moments.
"""

import os
from datetime import datetime
from moments.timestamp import Timestamp, Timerange
from moments.journal import log_action, load_journal, Journal

def load_instance(instances="/c/instances.txt", tag=None):
    """
    load instances.txt journal
    look for the newest entry with tag "default"
    return the data of the entry as a list of each file/line
    """
    j = load_journal(instances)
    if tag is not None:
        entries = j.tags[tag]
    else:
        entries = j
        
    #for sorting a list of entries:
    j2 = Journal()
    j2.from_entries(entries)
    entries = j2.sort_entries(sort='reverse-chronological')

    #should be the newest entry with tag "tag"
    e = entries[0]
    items = e.data.splitlines()
    #print items
    return items

def assemble_today(calendars="/c/calendars", destination="/c/outgoing", priority="/c/priority.txt", include_week=False):
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

    #CALENDAR LOADING:
    this_month_file = '%02d.txt' % now.month
    this_month_path = os.path.join(calendars, this_month_file)
    j = load_journal(this_month_path, ['calendar'])
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
        new_date = datetime(now.dt.year, e.created.month,
                            e.created.day, e.created.hour,
                            e.created.minute, e.created.second)
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
