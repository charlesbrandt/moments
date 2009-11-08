#!/usr/bin/env python
"""
#
# Description:

# read in an ical file.  convert all events to moments in a moment log

# By: Charles Brandt [code at contextiskey dot com]
# On: *2009.05.07 15:59:16 
# License:  MIT

# Requires: moments, medialist
#
# Sources:
#
# Thanks:
#
# TODO:


$Id$ (???)
"""
import sys, os
from moments.journal import Journal
from moments.log import Log
from moments.moment import Moment
from moments.timestamp import Timestamp
from icalendar import Calendar, Event

def from_ical(f1, trial_run=False, tags=['events'], annual=False):
    result = ''
    cal = Calendar.from_string(open(f1,'rb').read())
    #print cal

    now = Timestamp(now=True)

    for e in cal.walk('VEVENT'):
        ts = Timestamp()
        ts.from_apple_compact(str(e['DTSTART']))
        #print "*%s " % ts
        data = ''
        data += e['SUMMARY']
        if e.has_key('DESCRIPTION'):
            des = e['DESCRIPTION']
            des = des.strip()
            #print "->%s<-" % des
            #print "->%s<-" % des.strip("\n")
            #print "->%s<-" % des.strip()
            
            if e['SUMMARY'].strip() != des:
                from difflib import Differ
                from pprint import pprint
                d = Differ()
                result = list(d.compare([e['SUMMARY']], [des]))
                pprint(result)
                data += "\n%s" % e['DESCRIPTION']
        if e.has_key('LOCATION'):
            data += "\nLOCATION: %s" % e['LOCATION']
        if e.has_key('URL'):
            data += "\nURL: %s" % e['URL']
        #print data

        entry = Moment(data, tags, ts.time)
        print entry.render()

        if not trial_run:
            directory = './'
            fpath = ''
            #if we're not concerned about the year (as in birthdays),
            #force annual
            if annual:
                fname = "%02d-annual.txt" % ts.time.month
                fpath = os.path.join(directory, fname)
            else:
                if  ts.time.year != now.time.year:
                    #open local dir month file:
                    directory = "%s" % ts.time.year

                if not os.path.exists(directory):
                    print "making all directories for: %s" % directory
                    os.makedirs(directory)

                #add entry to month file of correct year:
                fname = "%02d.txt" % ts.time.month
                fpath = os.path.join(directory, fname)

            print fpath

            j = Journal()
            j.from_file(fpath)
            j.add_entry(entry)
            l = Log(fpath)
            l.from_entries(j.sort_entries(sort='chronological'))
            l.to_file()
            l.close()
        
        #print e.['']
        #print e.summary
        #print e.location
        #print e.url
        #print e.description
        #print component.name
    
    return result

def main():
    trial_run = False
    annual = False
    tags = ['events']
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            usage()

        if '-d' in sys.argv:
            pos = sys.argv.index("-d")
            sys.argv.remove("-d")
            trial_run = True
        if '-a' in sys.argv:
            pos = sys.argv.index("-a")
            sys.argv.remove("-a")
            annual = True
        if '--tags' in sys.argv:
            pos = sys.argv.index("--tags")
            sys.argv.remove("--tags")
            tag_string = sys.argv.pop(pos)
            tags = tag_string.split(',')

        f1 = sys.argv[1]

    from_ical(f1, trial_run, tags, annual)
        
if __name__ == '__main__':
    main()

#python ical/ical-from.py -d ical/iCal-imported_to_leopard-20080602/Sources/
#python ical/ical-from.py -d --tags car,transportation ical/iCal-imported_to_leopard-20080602/Sources/

#this is the main archive one it seems
#python ical/ical-from.py -d --tags archive ical/iCal-imported_to_leopard-20080602/Sources/50DA5325-9392-4AAA-B1B4-72A607827FFD.calendar/corestorage.ics
