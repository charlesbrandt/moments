#!/usr/bin/env python
"""
# Description:

# By: Charles Brandt [code at contextiskey dot com]
# On: 
# License:  MIT

# Requires: moments

open a log
report on the amount of time transpired between each entry

this should make it easy to remove blocks that are clearly not related to the project

should then be able to take that edited out put and compress it further into blocks... could group by day, by week, etc. (depending on reporting requirements)

"""
import sys, os

from moments.path import load_journal, Path
from moments.journal import Journal
from moments.timestamp import Timestamp

def log_minutes(j, destination=None):
    """
    create a separate log file that only contains the minutes involved
    can then merge them down accordingly by editing out close entries
    """
    last_stamp = None
    for e in j:
        if last_stamp:
            delta = e.created.dt - last_stamp.dt
            minutes = (delta.seconds / 60) + (delta.days * 24 * 60)
            e.data = "%s minutes (%s - %s)" % (minutes, last_stamp, e.created)
        last_stamp = e.created

    if destination:
        j.to_file(destination)

def format_minutes(j, skip=8):
    """
    
    """
    cur_year = None
    cur_month = None
    cur_day = None

    last_stamp = None
    total_minutes = 0
    for e in j:
        if e.created.year != cur_year:
            cur_year = e.created.year
            #print "%s" % cur_year
        if e.created.month != cur_month:
            cur_month = e.created.month
            #print "  %s" % cur_month
        if e.created.day != cur_day:
            cur_day = e.created.day
            print e.created.text(accuracy="day")

        if last_stamp:
            delta = e.created.dt - last_stamp.dt
            minutes = (delta.seconds / 60) + (delta.days * 24 * 60)
            if not minutes > skip*60:
                total_minutes += minutes
                print "%s minutes (%s - %s)" % (minutes, last_stamp, e.created)

        last_stamp = e.created

    hours = total_minutes / 60.0
    print "Total: %s minutes (%s hours)" % (total_minutes, hours)


def create_summary(source, destination):

    #j1 = load_journal('/c/clients/estella_vieira/journal.txt')
    j1 = load_journal(source)
    #j = j1.sort_entries('reverse-chronological')
    j = j1.sort_entries('chronological')
    #j = j1.sort_entries('reverse')

    #destination = '/c/clients/estella_vieira/summary.txt'

    #can comment out this to reformat summary:
    log_minutes(j, destination)
    j2 = load_journal(destination)
    j2 = j2.sort_entries('chronological')
    format_minutes(j2)
    
def main():
    if len(sys.argv) > 1:
        helps = ['--help', 'help', '-h']
        for i in helps:
            if i in sys.argv:
                usage()
                exit()

        f1 = sys.argv[1]
        if len(sys.argv) > 2:
            f2 = sys.argv[2]
        else:
            f1_path = Path(f1)
            f1_dir = f1_path.parent()
            
            f2 = os.path.join(str(f1_dir), "summary.txt")
            f2_path = Path(f2)
            if not f2_path.exists():
                print "Saving output to: %s" % f2
            else:
                print "Warning: %s exists!" % f2
                exit()

        create_summary(f1, f2)
        
if __name__ == '__main__':
    main()
