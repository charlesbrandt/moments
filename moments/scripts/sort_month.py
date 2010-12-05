#!/usr/bin/env python
"""
*2010.04.01 16:26:44
accept a month directory
go through all logs
and run sort_log.py on it (or equivalent function)
"""

import os, re, sys
from moments.path import Path
from moments.journal import Journal
from moments.log import Log

def main():
    if len(sys.argv) > 1:
        helps = ['--help', 'help', '-h']
        for i in helps:
            if i in sys.argv:
                usage()
                exit()

        #skip the first argument (filename):
        for arg in sys.argv[1:]:
            #arg should be something like: '/c/journal/2010/03'
            root = Path(arg)

            logs = os.listdir(str(root))
            for log in logs:
                l = Path(os.path.join(str(root), log))
                if l.extension == ".txt":
                    j = Journal()
                    j.from_file(l)
                    print len(j)

                    out = Log(str(l))
                    out.from_entries(j.sort_entries(sort="chronological"))
                    out.to_file()
                    out.close()

                    print l
                else:
                    #print "No: %s" % l
                    pass
        
if __name__ == '__main__':
    main()
