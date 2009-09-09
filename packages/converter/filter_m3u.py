#!/usr/bin/env python
"""
#
# Description:
# script to apply filters to an m3u file


# By: Charles Brandt [code at contextiskey dot com]
# On: 2009.03.22 11:59:13 
# License:  MIT

# Requires: moments, medialist
#

$Id$ (???)
"""
import sys, codecs, os.path
from moments.timestamp import Timestamp
from medialist.medialist import MediaList
from filters import *

def convert(src, dst="temp.txt"):
    result = ''

    #f = codecs.open(src, encoding='utf-8')
    #f = codecs.open(src)
    #f = open(src)


    #for line in f.readlines():
        #make an entry
    #    print line

    m = MediaList()
    m.from_m3u(src)
    m.multi_filter(path_updates)

    f = codecs.open(dst, 'w')
    f.write(m.to_m3u())
    f.close

    result = "File %s saved!" % dst
        
    print result
    
def main():
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            usage()
        f1 = sys.argv[1]
        if len(sys.argv) > 2:
            f2 = sys.argv[2]
        else:
            ts = Timestamp(now=True)
            parts = os.path.basename(f1).split('.')
            print parts
            f2 = parts[0] + "-filtered-" + ts.compact(accuracy='day') + '.' + parts[1]
        print f1
        convert(f1, f2)
        
if __name__ == '__main__':
    main()
