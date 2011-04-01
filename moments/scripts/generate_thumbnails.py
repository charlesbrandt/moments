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
#from moments.node import make_node
from moments.path import Path

def generate_thumbnails(src, rotate=False):
    path = Path(src)
    #node = make_node(src)
    if path.type() == "Directory":
        node = path.load()
        node.scan_directory()
        node.scan_filetypes()
        #node.scan_subdirs()
        
        dirs = node.directories
        #print node.directories
        for dpath in dirs:
            d = dpath.load()
            #not sure that we need this here:
            # this checks for existing thumbs, and skips generation if exists
            image_path = d.default_image()
            if image_path:
                image = image_path.load()
            else:
                image = None
                
            if image:
                size_path = image.size_path('tiny_o')
            else:
                size_path = None
            if (size_path and not os.path.exists(str(size_path))) or not size_path:

                d.create_journal()
                if rotate:
                    d.auto_rotate_images(update_thumbs=False)        
                print "generating thumbs for directory: %s" % d.path

                d.make_thumbs()

            else:
                print "skipping directory: %s" % d.path

        if rotate:
            node.auto_rotate_images(update_thumbs=False)        
        node.make_thumbs()
        print "All done!"
    else:
        print "Pass in a directory"
    
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
