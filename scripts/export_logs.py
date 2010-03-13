#!/usr/bin/env python
"""
#
# Description:

# takes two moment logs and merges them

# By: Charles Brandt [code at contextiskey dot com]
# On: 2009.01.29 18:15:01 
# License:  MIT

# Requires: moments
#
# Sources:
#
# Thanks:
#
# TODO:


$Id$ (???)
"""
import sys, subprocess, os, re

from moments.journal import Journal
from moments.tags import Tags
#from moments.node import make_node
from moments.path import Path
from merge_logs import merge_logs

def export_logs(source, destination, add_tags=[], recurse=True):
    """
    very similar to diff-directories functionality

    can't think of a good way to reuse at this point...
    going ahead with repeat
    """
    conflicts = []

    #src = make_node(source, relative=False)
    src = Path(source).load()
    src.scan_directory()
    #dst = make_node(destination, relative=False)
    dst = Path(destination).load()
    dst.scan_directory()
    dstcontents = dst.contents[:]

    print "items found: %s" % src.contents
    
    for i in src.contents:
        #items to ignore (and make sure it's a text file)
        if i not in [ "ignore_me.txt", ".hg", "README.txt" ] and re.search("\.txt", i):

            #print datetime.now()
            n1path = Path(os.path.join(source, i))
            n2path = Path(os.path.join(destination, i))

            print "exporting: %s" % i

            if i in dstcontents:
                #they both have an item with the same name

                dstcontents.remove(i)
                
                #n1 = make_node(n1path)
                #n2 = make_node(n2path)
                n1 = n1path.load()
                n2 = n2path.load()
                if n1path.type() == "Directory":
                    if recurse:
                        conflicts.extend(export_logs(n1, n2, add_tags, recurse))
                    else:
                        print "Not recursing into directory: %s" % n1
                else:
                    #must have 2 files... lets merge them
                    (merged, result) = merge_logs(n1path, n2path, add_tags)
                    if not result:
                        #must have been a problem in result (dupes)
                        #save for later
                        conflicts.append(merged)
                    else:
                        #merge came back with correct number of new entries
                        #lets remove the originals
                        #and rename the new one
                        #os.remove(str(n2path))
                        n2path.remove()
                        os.rename(merged, str(n2path))
                        #os.remove(n1path)
                        n1path.remove()
            else:
                # the file is in the source only
                # lets add tags (if any) then move the file to dst
                j = Journal()
                j.from_file(n1path, add_tags)
                j.to_file(n1path)

                #move might not work as in the case of pictures
                #os.rename(n1path, n2path)
                mv = subprocess.Popen("mv %s %s" % (n1path, n2path), shell=True, stdout=subprocess.PIPE)
                mv.wait()

    #if anything is left in dstcontents, it must not have been in src
    #in the case of an export, it's already on the destination... fin
    if len(dstcontents):
        pass

    return conflicts

def usage():
    print """
    python /c/code/python/scripts/export_logs.py outgoing/ /media/USB/outgoing/ system_name-other_tags

    """
    
def main():
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            usage()
        d1 = sys.argv[1]
        d2 = sys.argv[2]
        if len(sys.argv) > 3:
            #add_tags = tags_from_string(sys.argv[3])
            add_tags = Tags().from_tag_string(sys.argv[3])
        else:
            add_tags = []

        conflicts = export_logs(d1, d2, add_tags)
        for c in conflicts:
            print "Conflict found in: %s" % c
        
if __name__ == '__main__':
    main()
