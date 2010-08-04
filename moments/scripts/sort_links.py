#!/usr/bin/env python
"""
#
# Description:

# takes a moment log, finds all links,
# and saves a journal with the links sorted

# By: Charles Brandt [code at contextiskey dot com]
# On: 2009.01.29 18:15:01 
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

def order_links(f1, ofile="temp.txt"):
    result = ''
    
    j = Journal()
    j.from_file(f1)

    m = MediaList()

    for e in j:
        temp_m = MediaList()
        temp_m.from_copy_all_urls(e.data)
        updates = [ 
            ('dir\/', ''),
            ]

        temp_m.multi_filter(updates)

        #temp_m.from_relative()

        for i in temp_m:
            m.add_item(i)

    new_m = m.flatten_and_sort()

    result += "SAVING as: %s\n" % ofile
    new_m.to_file(ofile)
        
    print result
    
def main():
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            usage()
        f1 = sys.argv[1]
        order_links(f1)
        
if __name__ == '__main__':
    main()
