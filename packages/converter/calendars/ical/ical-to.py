#!/usr/bin/env python
"""
#
# Description:

# read in a moment log, convert all entries to an ical file

# By: Charles Brandt [code at contextiskey dot com]
# On: *2009.05.07 15:58:15 
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
import sys
from moments.journal import Journal
from medialist.medialist import MediaList

from icalendar import Calendar, Event
from icalendar import UTC # timezone
from datetime import datetime

def to_ical(f1, ofile="temp.txt"):
    result = ''
    cal = Calendar()
    cal.add('prodid', '-//Moments2iCal//contextiskey.com//')
    cal.add('version', '2.0')

    event = Event()
    event.add('summary', 'Python meeting about calendaring')
    event.add('dtstart', datetime(2005,4,4,8,0,0,tzinfo=UTC))
    event.add('dtend', datetime(2005,4,4,10,0,0,tzinfo=UTC))
    event.add('dtstamp', datetime(2005,4,4,0,10,0,tzinfo=UTC))
    event['uid'] = '20050115T101010/27346262376@mxm.dk'
    event.add('priority', 5)

    cal.add_component(event)

    f = open('example.ics', 'wb')
    f.write(cal.as_string())
    f.close()
    
    return result

def main():
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            usage()
        f1 = sys.argv[1]
        to_ical(f1)
        
if __name__ == '__main__':
    main()
