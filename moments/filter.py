#!/usr/bin/env python
"""
#
# Description:
walk the path, looking for moment logs
for each log
scan entries
for each entry
apply filter

# By: Charles Brandt [code at contextiskey dot com]
# On: *2009.09.11 18:52:31 
# License:  MIT

this functionality is implied many places:
/c/moments/scripts/filter_logs.py
/c/moments/scripts/split_by_day.py
/c/moments/scripts/make_m3u.py
/c/moments/packages/medialist/medialist/medialist.py
/c/moments/packages/medialist/medialist/filters.py
/c/moments/moments/extract.py
"""

import sys, os, re
from datetime import datetime
from journal import load_journal, Journal
from association import check_ignore

def filter_log(path, filters, save=False):
    """
    """
    if not os.path.isfile(path):
        raise ValueError, "path must be a file, got: %s" % path

    #j = Journal()
    #j.from_file(path)
    j = load_journal(path)
    
    j.filter_entries(filters)
    if save:
        #when it's time to save:
        j.to_file()


def filter_logs(path, updates=[], save=False):
    """
    """
    
    add_tags = []
    ignore_dirs = [ ]
    log_check = re.compile('.*\.txt$')
    if os.path.isdir(path):
        for root,dirs,files in os.walk(path):
            for f in files:
                if not log_check.search(f):
                    continue
                
                cur_file = os.path.join(root, f)
                if not check_ignore(cur_file, ignore_dirs):
                    filter_log(cur_file, updates, save)
                        
    elif os.path.isfile(path) and log_check.search(path):
        filter_log(path, updates, save)
    else:
        #no logs to scan
        print "Unknown filetype sent as path: %s" % path

    print "finished filtering"

def main():
    """
    """
    source = None
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            usage()
        source = sys.argv[1]

    updates = [ ['c\/media\/binaries', 'c/binaries'],
                ['^media\/', '/c/']
                ]
    filter_logs(source, updates, save=True)

if __name__ == '__main__':
    main()
