#!/usr/bin/env python
"""
#
# Description:
# use a moment log containing file paths to
# modify the path for local system
# and create a m3u file ( suitable for import into other media players )
# (note: it is better to use the logs themselves for players that support them)


# By: Charles Brandt [code at contextiskey dot com]
# On: 2009.07.25 11:32:11 
# License:  MIT

# Requires: moments

Example:
python /c/code/python/scripts/make_m3u.py /c/playlists/daily/2009/01/

# very similar to copy_media.py
# there is also similar functionality buried in Pose.

"""

import sys, os, re
import subprocess
from moments.journal import Journal, load_journal
from medialist.medialist import MediaList

def make_destination(source):
    #change the path used in logs to your local path
    #in this case, just remove the prefix /c/media
    #destination = source.replace('/c/media', '')
    
    #or can hard code it here (would flatten out everything sent)
    #destination = '/c/media/binaries/graphics/dwt/20090405-telepaths_show/shared/'

    #or just return the source: (no change needed for some playlists)
    destination = source
    return destination

def make_m3u(journal, output="temp.txt"):
    """
    """
    result = ''
    
    #j = Journal()
    #j.from_file(journal)
    j = load_journal(journal)
    m = MediaList()
    m.from_journal(j, local_path='/c')
    m3u = file(output, 'w')
    m3u.write("#EXTM3U\r\n")
    for i in m:
        if re.search('\.mp3', i):
            #obj = self.get_object(i)
            length = 0
            artist = ""
            title = os.path.basename(i)
            #this will cause iTunes to go with this string, rather than
            #reading ID3 tags and generating something more complete.
            #m3u.write("#EXTINF:%s,%s - %s\r\n" % (length, artist, title))
            m3u.write(i)
            m3u.write("\r\n")
    m3u.close()
    
def main():
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            usage()
        f1 = sys.argv[1]
        make_m3u(f1)
        
if __name__ == '__main__':
    main()
