from node import File

from ElementPList import load

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


class Library(File):
    """
    itunes XML library
    
    # Written By: Duncan McGreggor at 6:44 PM Tuesday, July 31, 2007
    # Import to Pose:
    # 2008.11.02 20:18
    #
    # Source:
    # http://oubiwann.blogspot.com/2007/07/export-itunes-playlists-as-m3u-files.html
    # License:
    # (I think this was GPL?)
    """
    def __init__(self, path, destDir=None):
        File.__init__(self, path)
        self.lib = None
        self.loadXML(path)
        self.destDir = destDir

    def loadXML(self, filename):
        self.lib = load(filename)

    def processTrack(self, trackData):
        m3uEntry = "#EXTINF:%(length)s,"
        m3uEntry += "%(artist)s - %(album)s - %(song)s\n%(filename)s\n"

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

    def processTrackIDs(self, ids):
        output = ''
        for id in ids:
            try:
                trackData = self.lib['Tracks'][str(id)]
                output += self.processTrack(trackData)
            except KeyError:
                print "Could not find track %i; skipping ..." % id
        return output

    def cleanName(self, unclean):
        clean = re.sub('[^\w]', '_', unclean)
        clean = re.sub('_{1,}', '_', clean)
        return clean

    def exportPlaylists(self):
        #moving create destDir down to export
        #that way it is not called unless we actually do the export
        if not self.destDir:
            #destDir = './'
            destDir = os.path.join(os.path.dirname(self.path),
                                   self.name_only + '_lists')
            if not os.path.isdir(destDir):
                os.mkdir(destDir)
            self.destDir = destDir

        m3uList = "#EXTM3U\n%s\n"
        exports = ''
        for playlist in self.lib['Playlists']:
            playlistName = self.cleanName(playlist['Name'])
            exports += playlistName + '\n'
            try:
                items = playlist['Playlist Items']
            except KeyError:
                print "Playlist seems to be empty; skipping ..."
                continue
            trackIDs = [x['Track ID'] for x in items]
            data = m3uList % self.processTrackIDs(trackIDs)
            fh = open("%s/%s.m3u" % (self.destDir, playlistName), 'w+')
            fh.write(data)
            fh.close
        return exports
