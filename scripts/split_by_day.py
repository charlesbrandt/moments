#!/usr/bin/env python
"""
#
# Description:
# script to run through a supplied directory's files
# create sub-directories that correspond to the day of the files' timestamps
# move the files to their corresponding day subdirectory
# in the new_dir destination

# By: Charles Brandt [code at contextiskey dot com]
# On: *2009.08.18 21:50:51 
# License:  MIT

# Requires: moments
#

$Id$ (???)
"""
import sys, os, subprocess
#from moments.node import Image, make_node
from moments.path import Path

def _move_files(source_dir, new_dir):
    """
    move all files on camera / usb media
    to local image directory
    """
    if not os.path.isdir(new_dir):
        os.mkdir(new_dir)

    #following yields:
    #OSError: [Errno 18] Cross-device link
    #on Mac OS X
    #may work elsewhere
    #result = ''
    #for item in d.contents:
    #    orig = os.path.join(d.path, item)
    #    new = os.path.join(new_dir, item)
    #    result += "%s %s\n" % (orig, new)
    #    os.rename(orig, new)

    source_dir = source_dir.replace(' ', '\ ')
    print source_dir

    #instead, just issue system command
    #for moving files
    command = "mv %s/* %s" % (source_dir, new_dir)
    mv = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    mv.wait()

    #for copying files
    command = 'cp %s/* %s' % (source_dir, new_dir)
    #mv = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)

    result = "All finished with moving files.  Any output included below:<br>\n"
    result += mv.stdout.read()
    result += "\n<br> All files moved to: %s" % new_dir
    result += "\n<br> Press Back to return <br> \n"

    return result

def _move_file(source, new_dir):
    """
    move all files on camera / usb media
    to local image directory
    """
    if not os.path.isdir(new_dir):
        os.mkdir(new_dir)

    path_string = str(source.path)
    source = path_string.replace(' ', '\ ')

    #instead, just issue system command
    #for moving files
    command = "mv %s %s" % (source, new_dir)
    mv = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    mv.wait()

    #for copying files
    #command = 'cp %s/* %s' % (source_dir, new_dir)
    #cp = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)

    result = "moving: %s" % source
    result += mv.stdout.read()

    return result

def _move_image_and_thumbs(source, new_dir):
    """
    move file the same as _move_file
    can be used to replace _move_file

    also, if file is an image,
    use os.rename to move thumbs in addition to image

    could consider migrating this to osbrowser.node.move
    """
    result = ''
    if not os.path.isdir(new_dir):
        os.mkdir(new_dir)

    path_string = str(source.path)
    source_path = path_string.replace(' ', '\ ')
    #source_path = source.path.replace(' ', '\ ')
    path = Path(source_path)
    source = path.load()
    #source = make_node(source.path)

    #instead, just issue system command
    #for moving files
    command = "mv %s %s" % (source_path, new_dir)
    mv = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    mv.wait()

    #for copying files
    #command = 'cp %s/* %s' % (source_path_dir, new_dir)
    #cp = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)

    result = "moving: %s" % source_path
    result += mv.stdout.read()


    #Try to move thumbnails if they exist
    if path.type() == "Image" and os.path.exists(source.thumb_dir_path):

        destination = os.path.join(new_dir, source.name)
        #new_file = make_node(destination)

        #move thumbnails
        new_image = Image(destination)

        #self.make_thumb_dirs(os.path.join(new_dir, self.thumb_dir_name))
        new_image.make_thumb_dirs()

        for k in source.sizes.keys():
            #may be some files/images that do not have thumbs.  check first
            if os.path.exists(source.size_path(k)):
                os.rename(source.size_path(k), new_image.size_path(k))
            else:
                result += "No thumb (size: %s) found for %s" % (k, source.path)


    #move any items in action.txt that are associated with the file
    if os.path.exists(os.path.join(os.path.dirname(source.path), 'action.txt')):
        print "don't forget to move items in action.txt!! :)"
        
    return result

def process_batch(batch, dest):
    for item in batch:
        #print _move_file(item, dest)
        print _move_image_and_thumbs(item, dest)
        #print item.date()

def split_by_day(path, dest_prefix=None):
    if dest_prefix is None:
        dest_prefix = path
    p = Path(path)
    d = p.load()
    #d = make_node(path)
    d.sort_by_date()
    
    dates = []
    destinations = []

    last_date = None
    cur_batch = []
    print "%s Files found in %s" % (len(d.files), path)
    for f in d.files:
        #print f.name
        if f.date() != last_date:
            #check if we need to move the previous day's files:
            if cur_batch:
                dest = os.path.join(dest_prefix, last_date)
                #print dest
                process_batch(cur_batch, dest)
                destinations.append(dest)

            cur_batch = [ f ]
            last_date = f.date()
        else:
            cur_batch.append(f)

    #get the last one:
    if cur_batch:
        #print cur_batch, last_date
        dest = os.path.join(dest_prefix, last_date)
        process_batch(cur_batch, dest)
        destinations.append(dest)

    #if we need to do something else to the new directories
    #we have them all collected in destinations list

    return destinations

def main():
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            usage()
        f1 = sys.argv[1]
        print f1
        split_by_day(f1)
        
if __name__ == '__main__':
    main()
