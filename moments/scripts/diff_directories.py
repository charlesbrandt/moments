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

#http://docs.python.org/release/2.5.2/lib/module-difflib.html
from difflib import Differ, unified_diff
from pprint import pprint

from moments.path import Path
#from osbrowser.library import phraseUnicode2ASCII
from moments.ascii import unaccented_map

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
    p1 = Path(path1)
    n1 = p1.load()
    #n1 = make_node(path1)

    p2 = Path(path2)
    n2 = p2.load()
    #n2 = make_node(path2)

    if n1.size == n2.size:
        #probably pretty safe to assume that they are equal
        #print " %s - BOTH, SAME SIZE" % phraseUnicode2ASCII(fname)
        #print "EQUAL sizes: %s %s" % (n1.size, n2.size)
        is_difference = False

        #could do additional checks if desired
        #enabling another diff level will take longer, but will be more accurate:
        f_a = file(path1)
        f_b = file(path2)
        a = f_a.readlines()
        b = f_b.readlines()
        diff = unified_diff(a, b)
        for d in diff:
            is_difference = True
            #print d

        #this will signal which files have differences:
        if is_difference:
            print " %s - BOTH, DIFFERENT CONTENT" % fname.translate(unaccented_map())
            
        #could move it somewhere else:
        #os.rename(path1, os.path.join(d1, "dupes", fname))
        #os.rename(path2, os.path.join(d2, "merged", fname))

    else:
        #print " %s - BOTH, DIFFERENT SIZE" % phraseUnicode2ASCII(fname)
        print " %s - BOTH, DIFFERENT SIZE" % fname.translate(unaccented_map())
        if diff_system:
            print "diffing: %s %s\n" % (path1, path2)
            try:
                #diff_system( phraseUnicode2ASCII(path1),
                #             phraseUnicode2ASCII(path2) )
                #diff_playlists(n1, n2)
                diff_system( path1.translate(unaccented_map()),
                             path2.translate(unaccented_map()) )
            except:
                print "Unable to diff."

    return is_difference



def diff_dirs(dpath1, dpath2, recurse=True, indent=0, show_both=False ):
    
    is_difference = False

    p1 = Path(dpath1)
    d1 = p1.load()
    #d1 = make_node(dpath1, relative=False)
    d1.scan_directory()

    p2 = Path(dpath2)
    d2 = p2.load()
    #d2 = make_node(dpath2, relative=False)
    d2.scan_directory()
    d2contents = d2.listdir[:]
    
    for i in d1.listdir:
        #items to ignore:
        if i not in [ "ignore_me.txt", ".hg" ]:

            #print datetime.now()
            n1path = os.path.join(dpath1, i)
            n2path = os.path.join(dpath2, i)

            if i in d2contents:
                #they both have an item with the same name

                d2contents.remove(i)
                if show_both:
                    #print "%s - BOTH" % phraseUnicode2ASCII(i)
                    print "%s - BOTH" % i.translate(unaccented_map())
                
                p1 = Path(n1path)
                n1 = p1.load()
                #n1 = make_node(n1path)
                p2 = Path(n2path)
                n2 = p2.load()
                #n2 = make_node(n2path)
                if p1.type() == "Directory":
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
                print "%s - D1 ONLY" % i.translate(unaccented_map())
                #could move it if desired:
                #os.rename(n1path, n2path)

    #if anything is left in d2contents, it must not have been in d1
    if len(d2contents):
        is_difference = True
        for i in d2contents:
            print "%s - D2 ONLY" % i.translate(unaccented_map())

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
