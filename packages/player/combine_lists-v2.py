#!/usr/bin/env python
"""
# Description:

# parse a file with -ss ####  or -sl commands
# split it into entries using moments.log.Log

# By: Charles Brandt [code at contextiskey dot com]
# On: *2009.06.04 15:29:27 
# License:  MIT
"""
import sys,os,re
from moments.log import Log
from moments.entry import Entry

def sync_list(f1, f2=None, save=False):
    """
    parse the file as a (new-style) Log
    """
    efile = Log(f1)
    efile.from_file()
    entries = efile.to_entries()
    new_entries = []
    
    for e in entries:
        have_sl = False
        sl = ''
        
        for line in e.data.splitlines():
            if re.search("-sl", line):
                have_sl = True
                sl = line
                new_e = Entry(tags=e.tags)
                new_e.data = sl + '\n'
                new_entries.append(new_e)

    return new_entries

def main():
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            usage()
        path = sys.argv[1]

        merge_all = True
        if os.path.isdir(path):
            sls = []
            #look for all files in the directory that contain edit lists (.txt)
            #parse each of those:
            print "scanning path: %s" % path
            files = os.listdir(unicode(path))
            for f in files:
                extension = os.path.splitext(f)[1]
                fpath = os.path.join(path, f)                
                if extension == ".txt":
                    #print "scanning file: %s, with extension: %s" % (fpath, extension)
                    
                    entries = sync_list(fpath, save=True)
                    sls.extend(entries)
            if merge_all:
                efile = Log("combine-list.txt")
                #output = open("temp.txt", 'w')
                #output.writelines(sls)
                efile.from_entries(sls)
                efile.to_file()
            
        else:
            sync_list(path, save=True)
        
if __name__ == '__main__':
    main()
