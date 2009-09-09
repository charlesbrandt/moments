#!/usr/bin/env python
"""
#
# Description:

# takes a text/unicode file that was exported from itunes
# skip first (header) line
# for each line after, create entry
# exports all entries to a corresponding moment log


# By: Charles Brandt [code at contextiskey dot com]
# On: 2009.03.21 10:47:04 
# License:  MIT

# Requires: moments, medialist
#
# 2009.03.22 06:00:43 
# this ended up being a real pain with no newlines, and the tabs being difficult to split on... going back to xml
# see itunes_xml_to_log.py

$Id$ (???)
"""
import sys, codecs
from moments.journal import Journal
from medialist.medialist import MediaList

def convert(src, dst="temp.txt"):
    result = ''

    #f = codecs.open(src, encoding='utf-8')
    f = codecs.open(src)
    #f = open(src)

    #for itunes files, this is everything.. no newlines apparently... bah
    first = f.readline()
    #print first

    parts = first.split(r"\t")

    for p in parts:
        print str(p)
    
    for line in f.readlines():
        #make an entry
        print line
    
##     m = MediaList()

##     for e in entries:
##         temp_m = MediaList()
##         temp_m.from_copy_all_urls(e.data)
##         updates = [ 
##             ('dir\/', ''),
##             ]

##         temp_m.multi_filter(updates)

##         #temp_m.from_relative()

##         for i in temp_m:
##             m.add_item(i)

##     new_m = m.flatten_and_sort()

##     result += "SAVING as: %s\n" % ofile
##     new_m.to_file(ofile)
        
    print result
    
def main():
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            usage()
        f1 = sys.argv[1]
        if len(sys.argv) > 2:
            f2 = sys.argv[2]
        else:
            f2 = f1 + ".log"
        print f1
        convert(f1, f2)
        
if __name__ == '__main__':
    main()
