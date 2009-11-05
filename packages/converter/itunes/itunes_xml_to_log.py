#!python
#
# Written By: Duncan McGreggor at 6:44 PM Tuesday, July 31, 2007
# Imported By: Charles Brandt
# On: 2008.02.18 00:46
#
# Source:
# http://oubiwann.blogspot.com/2007/07/export-itunes-playlists-as-m3u-files.html
#
# Description:
# code to convert itune library to m3u files.
#
# With usage like the following:  (assuming filename of iTunesExport)
#
#>>> from iTunesExport import exportPlaylists
#>>> BASE = "/Volumes/itunes/__Playlists__"
#>>> exportPlaylists('%s/Library.xml' % BASE, BASE)

import os
import sys

import re

import urllib

from ElementPList import load
from datetime import datetime
from moments.moment import Moment
from moments.log import Log
from moments.timestamp import Timestamp

m3uList = "#EXTM3U\n%s\n"
m3uEntry = "#EXTINF:%(length)s,"
m3uEntry += "%(artist)s - %(album)s - %(song)s\n%(filename)s\n"

def phraseUnicode2ASCII(message):
    """
    Works around the built-in function str(message) which aborts when non-ASCII
    unicode characters are given to it.

    Modified from http://mail.python.org/pipermail/python-list/2002-June/150077.html
    """
    try:
        newMsg = message.encode('ascii')
    except (UnicodeDecodeError, UnicodeEncodeError):
       chars=[]
       for uc in message:
          try:
             char = uc.encode('ascii')
             chars.append(char)
          except (UnicodeDecodeError, UnicodeEncodeError):
             pass
       newMsg = ''.join(chars)
    return newMsg.strip()

class Playlists(object):

    def __init__(self, filename=None, destDir=None):
        self.lib = None
        if filename:
            self.lib = load(filename)
            #def loadXML(self, filename):
            #contained: self.lib = load(filename)
            #and was called here:
            #self.loadXML(filename)
        if not destDir:
            destDir = './'
        self.destDir = destDir


    def processTrack(self, trackData):
        length = trackData.get('Total Time') or 300000
        song = trackData.get('Name') or 'Unknown'
        artist = trackData.get('Artist') or 'Unknown'
        album = trackData.get('Album') or 'Unknown'
        data = {
            'filename': trackData['Location'],
            'length': int(length)  / 1000 + 1,
            'song': phraseUnicode2ASCII(song),
            'artist': phraseUnicode2ASCII(artist),
            'album': phraseUnicode2ASCII(album),
        }
        return m3uEntry % data

    def track_to_entry(self, trackData):
        last_played = trackData.get('Play Date UTC')
        #length = trackData.get('Total Time') or 300000
        #song = trackData.get('Name') or 'Unknown'
        #artist = trackData.get('Artist') or 'Unknown'
        #album = trackData.get('Album') or 'Unknown'

        e = Moment()
        loc = urllib.unquote(trackData['Location'])
        loc = loc.replace(r'file://localhost/Volumes/Binaries/', 'media/binaries/')
        e.data = loc
        #print last_played
        if last_played:
            e.created = Timestamp().from_text(last_played)
        else:
            e.created = Timestamp()
        e.tags = [ 'sound', 'play', 'itunes' ]
        return e
    
    def cleanName(self, unclean):
        clean = re.sub('[^\w]', '_', unclean)
        clean = re.sub('_{1,}', '_', clean)
        return clean

    def exportPlaylists(self, format="log", destination=None):
        for playlist in self.lib['Playlists']:
            playlistName = self.cleanName(playlist['Name'])
            try:
                items = playlist['Playlist Items']
            except KeyError:
                print "Playlist seems to be empty; skipping ..."
                continue

            ids = [x['Track ID'] for x in items]
            output = ''
            entries = []
            for id in ids:
                try:
                    trackData = self.lib['Tracks'][str(id)]
                    if format == "log":
                        entries.append(self.track_to_entry(trackData))
                    else:
                        output += self.processTrack(trackData)
                        
                except KeyError:
                    print "Could not find track %i; skipping ..." % id

            if format == "log":
                if destination:
                    l = Log(destination)
                else:
                    l = Log("%s/%s.txt" % (self.destDir, playlistName))
                l.from_entries(entries)
                l.to_file()

            else:
                data = m3uList % output
                fh = open("%s/%s.m3u" % (self.destDir, playlistName), 'w+')
                fh.write(data)
                fh.close


#pls = Playlists("/home/charles/charles/media/binaries/music-other/itunes_library_backups/20081027-powerbook-tessas_account/iTunes Music Library.xml", "playlists/")
#pls.exportPlaylists()

def usage():
    print "Something to the effect of:"
    print "python itunes_xml_to_log.py --input /c/playlists/from_software/Recently\ Played-20090322.xml --output test.txt"
    

def main():
    input = None
    output = None
    dest = None
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 4:
            usage()
        iter = 1
        while iter < len(sys.argv):
            if sys.argv[iter] in ['--input'] and iter+1 < len(sys.argv):
                print "INPUT: " + sys.argv[iter+1]
                input = sys.argv[iter+1]
                iter = iter + 1
            elif sys.argv[iter] in ['--output'] and iter+1 < len(sys.argv):
                print "OUTPUT: " + sys.argv[iter+1]
                output = sys.argv[iter+1]
                iter = iter + 1
            else:
                print "Error: unknown parameter: " + sys.argv[iter]
                sys.exit(0)
            iter = iter + 1

    now = Timestamp(now=True)
    today = now.compact(accuracy='day')
    if input:
        filename = input
    else:
        filename = '/c/playlists/from_software/itunes/recently_played/%s.xml' % today

    if output:
        dest = output
    else:
        dest = '/c/playlists/daily/transfer/%s.txt' % today

    if os.path.exists(dest):
        print "FILE EXISTS: %s" % dest
        exit()
        
    pls = Playlists(filename)
    pls.exportPlaylists(destination=dest)


if __name__ == '__main__':
    main()

