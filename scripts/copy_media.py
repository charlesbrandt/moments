#!/usr/bin/env python
"""
#
# Description:
# use a moment log containing local file paths to
# copy the source files to a new directory
#


# By: Charles Brandt [code at contextiskey dot com]
# On: 2009.04.13 20:13:01 
# Also: 2009.07.25 10:23:48 
# License:  MIT

# Requires: moments

Example:
python /c/code/python/scripts/copy_media.py /c/playlists/daily/2009/01/ /c/media:/c

the last parameter is a translate, filter option
the prefix in place in all source logs is the first option
and the local destination is the second option

TODO:
convert to using medialist.sources
"""

import sys, os, re
import subprocess
from moments.journal import Journal, load_journal
from moments.association import check_ignore
#from medialist.medialist import MediaList
from medialist.sources import Converter, Sources

def flatten_structure(source):
    destination = '/binaries/music/vinyl/flat/'
    ignore_dirs = [ 'downloads' ]
    all_audio = []
    mp3_check = re.compile('.*\.mp3$')
    if os.path.isdir(source):
        for root,dirs,files in os.walk(source):
            for f in files:
                if not mp3_check.search(f):
                    continue

                if not check_ignore(os.path.join(root, f), ignore_dirs):
                    all_audio.append(os.path.join(root, f))

    elif os.path.isfile(source) and mp3_check.search(source):
        all_audio.append(source)

    print "found the following audio files in path: %s" % source
    print all_audio
    for f in all_audio:
        print "copying: %s" % f
        copy_file(f, destination)
    

def make_destination(source, translate):
    if translate is not None:
        (pre, post) = translate.split(':')
    else:
        (pre, post) = ('/c/media', '')

    destination = source.replace(pre, post)
    print "destination: %s" % destination
    
    #change the path used in logs to your local path
    #in this case, just remove the prefix /c/media
    #destination = source.replace('/c/media', '')
    #or can hard code it here (would flatten out everything sent)
    #destination = '/c/media/binaries/graphics/dwt/20090405-telepaths_show/shared/'

    #filename = os.path.basename(source)
    #destination = '/c/trial/off/' + filename
    
    return destination

def copy_file(source, destination):
    """
    copy a single file 
    """
    #cp = subprocess.Popen("cp %s %s" % (source, destination), shell=True, stdout=subprocess.PIPE)
    #cp.wait()
    command = 'rsync -av "%s" "%s"' % (source, destination)
    print command
    rsync = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print rsync.communicate()[0]


def copy_files(journal, translate=None):
    """
    copy *only* the files referenced in a journal to a new loacation
    """
    result = ''
    
    #j = Journal()
    #j.from_file(journal)
    j = load_journal(journal)
    #m = MediaList()
    #m.from_journal(j, local_path='/c')
    sources = Sources()
    converter = Converter(sources)
    converter.from_entries(j)
    for i in sources:
        print i
        if re.search('\.mp3', i.path):
            destination = make_destination(i.path, translate)
            #print "SOURCE: %s" % i
            #print "DEST: %s" % destination

            if os.path.exists(destination):
                print "skipping: %s" % destination
            else:
                dest_path = os.path.dirname(destination)
                if not os.path.exists(dest_path):
                    os.makedirs(dest_path)

                copy_file(i.path, destination)
    
def main():
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            usage()
        f1 = sys.argv[1]
        translate = None
        if len(sys.argv) > 2:
            translate = sys.argv[2]
        copy_files(f1, translate)

def flatten():
    source = sys.argv[1]
    flatten_structure(source)
    
if __name__ == '__main__':
    main()
    #flatten()
