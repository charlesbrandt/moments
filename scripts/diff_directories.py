#!/usr/bin/env python
"""
#
# Description:

# takes two directory paths as input
# looks at the contents of both directories
# and recursively finds files with differences between the two of them

# By: Charles Brandt [code at contextiskey dot com]
# On: 2009.01.15 12:53:14
# License:  MIT

# Requires: osbrowser python module
#
# Sources:
#
# Thanks:
#
# TODO:


$Id$ (???)
"""

# skelton for command line interaction:
import os, sys
import re
import subprocess
from datetime import datetime

from difflib import Differ
from pprint import pprint

from osbrowser import make_node
from osbrowser.library import phraseUnicode2ASCII

VAR = None

def usage():
    print "Description from header would be cool here"

def diff_system(path1, path2):
    #this will show differences if cases are different:
    #i.e. MUSIC != Music
    #case sensitive:

    diff = subprocess.Popen(["diff", path1, path2], stdout=subprocess.PIPE).communicate()[0]
    print "DIFF OUTPUT:"
    print diff


def diff_playlists(path1, path2):
    #moved to different script for better memory usage
    diff = subprocess.Popen(["./diff-playlists.py", n1path, n2path], stdout=subprocess.PIPE).communicate()[0]
    print "DIFF OUTPUT:"
    print diff

def diff_files(fname, path1, path2, indent, diff_system=False):

    #until we prove otherwise, we'll assume they're different
    is_difference = True
    n1 = make_node(path1)
    n2 = make_node(path2)

    if n1.size == n2.size:
        #print " %s - BOTH, SAME SIZE" % phraseUnicode2ASCII(fname)
        is_difference = False

        #probably pretty safe to assume that they are equal
        #print "EQUAL sizes: %s %s" % (n1.size, n2.size)

        #could do additional checks if desired

        #could move it somewhere else:
        #os.rename(path1, os.path.join(d1, "dupes", fname))
        #os.rename(path2, os.path.join(d2, "merged", fname))

        pass

    else:
        print " %s - BOTH, DIFFERENT SIZE" % phraseUnicode2ASCII(fname)
        if diff_system:
            print "diffing: %s %s\n" % (path1, path2)
            try:
                diff_system( phraseUnicode2ASCII(path1),
                             phraseUnicode2ASCII(path2) )
                #diff_playlists(n1, n2)
            except:
                print "Unable to diff."

    return is_difference



def diff_dirs(dpath1, dpath2, recurse=True, indent=0, show_both=False ):
    
    is_difference = False

    d1 = make_node(dpath1, relative=False)
    d1.scan_directory()
    d2 = make_node(dpath2, relative=False)
    d2.scan_directory()
    d2contents = d2.contents[:]
    
    for i in d1.contents:
        #items to ignore:
        if i not in [ "ignore_me.txt", ".hg" ]:

            #print datetime.now()
            n1path = os.path.join(dpath1, i)
            n2path = os.path.join(dpath2, i)

            if i in d2contents:
                #they both have an item with the same name

                d2contents.remove(i)
                if show_both:
                    print "%s - BOTH" % phraseUnicode2ASCII(i)
                
                n1 = make_node(n1path)
                n2 = make_node(n2path)
                if n1.find_type() == "Directory":
                    if recurse:
                        last_difference = diff_dirs(n1path, n2path, recurse, indent+1)
                        is_difference |= last_difference
                        if last_difference:
                            print "Differences found: %s" % n1path
                            #add a new line after finished with 
                            if not indent:
                                print "\n"
                    else:
                        print "No Comparison"
                else:
                    is_difference |= diff_files(i, n1path, n2path, indent)

            else:
                is_difference = True
                print "%s - D1 ONLY" % phraseUnicode2ASCII(i)
                #could move it if desired:
                #os.rename(n1path, n2path)

    #if anything is left in d2contents, it must not have been in d1
    if len(d2contents):
        is_difference = True
        for i in d2contents:
            print "%s - D2 ONLY" % phraseUnicode2ASCII(i)

    return is_difference

def main():
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            usage()
        d1 = sys.argv[1]
        d2 = sys.argv[2]
        diff_dirs(d1, d2)
        
if __name__ == '__main__':
    main()
