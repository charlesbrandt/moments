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
        last_content = ''
        have_sl = False
        jumps = []
        sl_jumps = []
        sl = ''
        cur_data = ''
        
        for line in e.data.splitlines():
            if re.search("-sl", line):
                have_sl = True
                sl = line
                parts = line.split(" ", 3)
                sl_jumps = parts[2]
                last_content = parts[3]
            elif re.search("-ss", line):
                if re.match("#", line):
                    #print "FOUND SS LINE STARTING WITH #: %s" % line
                    parts = line.split(" ", 3)
                    #get rid of leading "#"
                    parts = parts[1:]
                else:
                    parts = line.split(" ", 2)
                #see if we're still working with the same media file:

                if parts[2] != last_content:
                    #something new

                    #make sure we had something (i.e. not first update)
                    if last_content:
                        print "different items in same entry!!"
                        #make new entry
                        new_e = Entry(tags=e.tags)
                        if not have_sl and jumps:
                            sl = "# -sl %s %s\n" % (','.join(jumps), last_content)
                            new_e.data = sl + cur_data
                        else:
                            new_e.data = cur_data
                        new_entries.append(new_e)
                        cur_data = ''
                        jumps = []
                        
                    last_content = parts[2]
                    jumps = [ parts[1] ]
                else:
                    jumps.append(parts[1])
            cur_data += line + '\n'

        if not have_sl and jumps:
            print "adding in SL"
            sl = "# -sl %s %s\n" % (','.join(jumps), last_content)
            e.data = sl + cur_data

        new_entries.append(e)

    #for e in new_entries:
    #    print ">>>\n%s\n<<<\n" % e.render()
    efile.from_entries(new_entries)
    efile.to_file()

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
                    
                    sync_list(fpath, save=True)

            if merge_all:
                output = open("temp.txt", 'w')
                output.writelines(sls)
            
        else:
            sync_list(path, save=True)
        
if __name__ == '__main__':
    main()
