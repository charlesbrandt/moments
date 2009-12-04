#!/usr/bin/env python
"""
#
# Description:
# script to run through a supplied directory's sub directory and generate
# all thumbnails using moments.node
# this way they will be ready for future browsing.


# By: Charles Brandt [code at contextiskey dot com]
# On: *2009.06.10 07:41:07 
# License:  MIT

# Requires: moments
#

$Id$ (???)
"""
import sys, codecs, os.path
from moments.node import make_node

def generate_thumbnails(src, rotate=False):
    node = make_node(src)
    node.scan_directory()
    node.scan_filetypes()

    dirs = node.directories
    #print node.directories
    for d in dirs:
        if rotate:
            d.auto_rotate_images(update_thumbs=False)        
        print "generating thumbs for directory: %s" % d.name
        d.make_thumbs()
        
    if rotate:
        node.auto_rotate_images(update_thumbs=False)        
    node.make_thumbs()
    print "All done!"
    
def main():
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            usage()
        if '-r' in sys.argv:
            sys.argv.remove('-r')
            rotate = True
            print "Rotating first"
        else:
            rotate = False
        f1 = sys.argv[1]
        print f1
        generate_thumbnails(f1, rotate)
        
if __name__ == '__main__':
    main()
