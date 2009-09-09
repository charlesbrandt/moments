#!/usr/bin/env python
"""
# Description:

# take a directory with images in sub directories
# make a mplayer playlist, in addition to a second list for each subdirectory

# By: Charles Brandt [code at contextiskey dot com]
# On: *2009.04.30 15:55:18 
# License:  MIT

# Requires: osbrowser
#
# TODO:
"""
import sys,os
from osbrowser.meta import make_node

def jump_string(jumps):
    temp = []
    for j in jumps:
        if j not in temp:
            temp.append(str(j))
    jump_string = ','.join(temp)
    #print ""
    #print jump_string        

    return jump_string


def scan_images(node):
    """
    helper function...
    takes a directory,
    scans for images in that directory
    makes a jump list from them
    returns the list
    """
    node.scan_directory()
    node.scan_filetypes()

    images = node.images
    jumps = []
    for i in images:
        seconds = i.name[:4]
        if int(seconds) not in jumps:
            jumps.append(int(seconds))
    jumps.sort()
    return jumps
    

def make_lists(d1, ofile="temp.txt", relative=True):
    """
    #accept a directory with the images
    #images should be in subdirectories according to tags
    #for each subdirectory
    #generate the list of times (-sl)
    
    #also make a header with all tags (except s# ones)
    """
    result = ''

    all_tags = []

    ## if relative:
    ##     node = make_node(os.path.join(os.path.dirname(__file__), d1))
    ## else:
    node = make_node(d1)
        
    
    print "Scanning directory: %s" % node.path
    
    top_jumps = scan_images(node)
    if top_jumps:
        result += '* -sl %s ""\n\n' % (jump_string(top_jumps))


    for d in node.sub_directories:
        #print "Scanning subdirectory: %s : %s" % (d.name, d.path)
        jumps = scan_images(d)
        #print jumps
        if jumps:
            tags = d.name.split('-')
            #ok if there are dupes here:
            all_tags.extend(tags)
            result += '* %s\n' % (' '.join(tags))
            result += '* -sl %s ""\n\n' % (jump_string(jumps))

    #if changing these, 
    #don't forget to update ignores in distribute_blocks too:
    ignores = set(['intro', 's1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10', 'cd2', 'cd3', 'cd4'])
    unordered = set(all_tags).difference(ignores)

    #restore order
    relevant_tags = []
    for i in all_tags:
        if i in unordered:
            relevant_tags.append(i)
        
    first_line = "* %s\n" % ' '.join(relevant_tags)
    result = first_line + result
    
    f = open(ofile, 'w')
    f.write(result)
    f.close()

    print "finished processing\n"
    print
    print "don't forget to:"
    print " -add the correct source files to temp.txt"
    print " -remove duplicate times by watching result"
    print
    print "before running expand_lists.py"
    
def main():
    f1 = ''
    try:
        f = open("processing.txt")
        data = f.read()
        f.close()
        lines = data.splitlines()
        f1 = lines[0]
    except:
        print "could not read processing.txt"
        
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            usage()

        ## pos = sys.argv.index("-images")
        ## sys.argv.remove("-images")

        ## #should be relative to this file:
        ## image_dir = sys.argv.pop(pos)

        f1 = sys.argv[1]

    if f1:
        make_lists(f1)
    else:
        print "unknown directory to process"
        
if __name__ == '__main__':
    main()
