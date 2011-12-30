#!/usr/bin/env python
"""
# Description:

# functions for merging two moment logs 
# and exporting groups of files and automatically merging those

# By: Charles Brandt [code at contextiskey dot com]
# On: 2009.01.29 18:15:01 
# License:  MIT

# Requires: moments
"""
import sys, subprocess, os, re

from moments.journal import Journal
from moments.tag import Tags
from moments.path import Path, load_journal
from moments.timestamp import Timestamp

def merge_many(source, destination, add_tags=[]):
    """
    use load journal to load the source directory
    then save the resulting journal to the temporary destination
    """
    j = load_journal(source, add_tags)
    j.sort_entries('reverse-chronlological')
    j.to_file(destination)
    
def merge_logs(f1, f2, add_tags=[], ofile="", verbose=False):
    """
    this is a common operation involving two log files or two Journal objects

    it is fairly simple with the Journal object,
    but this handles all of the calls
    for creating those Journal objects from files
    
    add tags will only apply to the first file
    it is being merged into the second
    """
    #shouldn't need osbrowser here... we know the absolute paths via shellx
    #n1 = osbrowser.meta.make_node(f1)

    result = ''
    
    j = Journal()
    j.load(f1, add_tags)
    len1 = len(j.entries())
    
    j2 = Journal()
    j2.load(f2)
    len2 = len(j2.entries())

    j.load(f2)
    len3 = len(j.entries())
    
    result += "merge resulted in %s entries from %s and %s\n" % (len3, len1, len2)

    f2_obj = Path(f2)
    if not ofile:
        now = Timestamp(now=True)
        temp_name = "merge-%s-%s.txt" % (now.compact(), f2_obj.name)
        ofile = os.path.join(str(f2_obj.parent()), temp_name)
    result += "SAVING as: %s\n" % ofile
    j.save(ofile)

    if verbose:
        print result

    #if there are dupes the two totals may not add up to the new total
    # (does not necessarily mean a conflict)
    #and now journal can handle multiple entries with the same timestamp,
    # (so it will not discard subsequent entries with the same timestamp)
    #so it may be ok to always accept a merge
    # (as long as both files consisted of actual moment entries)
    #
    #if (len1+len2 == len3):
    #    return (ofile, 1)        
    #else:
    #    result += "WARNING: dupes/conflicts encountered<br>"
    #    return (ofile, 0)

    return (ofile, 1)


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
    dstlistdircp = dst.listdir[:]

    print "items found: %s" % src.listdir
    
    for i in src.listdir:
        #items to ignore (and make sure it's a text file)
        if i not in [ "ignore_me.txt", ".hg", "README.txt" ] and re.search("\.txt", i):

            #print datetime.now()
            n1path = Path(os.path.join(source, i)) # == i ???
            n2path = Path(os.path.join(destination, i))

            print "exporting: %s" % i

            if i in dstlistdircp:
                #they both have an item with the same name

                dstlistdircp.remove(i)
                
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
                j.load(n1path, add_tags)
                j.save(n1path)

                if os.name == "nt":
                    #move might not work as in the case of pictures
                    os.rename(str(n1path), str(n2path))
                else:
                    #on posix type systems this is more likely to work
                    #between different devices
                    mv = subprocess.Popen("mv %s %s" % (n1path, n2path), shell=True, stdout=subprocess.PIPE)
                    mv.wait()

    #if anything is left in dstlistdircp, it must not have been in src
    #in the case of an export, it's already on the destination... fine
    if len(dstlistdircp):
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
        
        # for merging
        # f1 = sys.argv[1]
        # f2 = sys.argv[2]
        # merge_logs(f1, f2, verbose=True)

if __name__ == '__main__':
    main()
