#!/usr/bin/env python
"""
# Description:

# read processing.txt
# to get the name of the directory storing images
# and last directory created
#
# then move all images to last directory create
# make a new directory based on argument
# then save the new directory name in processing.txt

# By: Charles Brandt [code at contextiskey dot com]
# On: *2009.05.01 18:23:01 
# License:  MIT

# Requires: 
"""
import sys,os,re
from osbrowser.meta import make_node

def main():
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            usage()

        new_dir = sys.argv[1]

        # read processing.txt
        f = open("processing.txt")
        data = f.read()
        f.close()
        
        lines = data.splitlines()
        # get the name of the directory storing images
        working_dir = lines[0]
        # and last directory created
        previous_dir = lines[1]

        # then move all images to last directory created
        node = make_node("/c/other")
        node.scan_directory()
        node.scan_filetypes()

        if not os.path.exists(os.path.join(working_dir, previous_dir)):
            os.makedirs(os.path.join(working_dir, previous_dir))
        #if not os.path.exists(working_dir):
        #    os.makedirs(working_dir)
            

        images = node.images
        for i in images:
            #print i.path
            #print working_dir
            #print previous_dir
            #print i.name
            #print os.path.join(working_dir, previous_dir, i.name)
            #print

            #this check is a kludge
            #since images are being listed multiple times
            #in osbrowser.node.directory
            if os.path.exists(i.path):
                os.rename(i.path, os.path.join(working_dir, previous_dir, i.name))
            
        # make a new directory based on argument
        if not os.path.exists(os.path.join(working_dir, new_dir)):
            os.makedirs(os.path.join(working_dir, new_dir))
            
        # then save the new directory name in processing.txt
        f = open("processing.txt", 'w')
        f.write("%s\n%s" % (working_dir, new_dir))
        f.close()
        
if __name__ == '__main__':
    main()
