#!/usr/bin/python
#
# Converts an Apple iTunes Music Library.xml file into a set of .m3u
# playlists.
#
# Copyright (C) 2006 Mark Huang <mark.l.huang@gmail.com>
# License is GPL
#
# $Id: itunes2m3u.py,v 1.1 2006/07/05 05:24:42 mlhuang Exp $
#

# 2008.08.25 13:28
# initial tests some time ago didn't seem to work with this script
# see convert_itunes_to_m3u.py

import os
import sys
import getopt
import xml.sax.handler
import pprint
import base64
import datetime
import urlparse
import codecs
import array
import re

# Defaults

# Encoding of track and file names in .m3u files. Escaped 8-bit
# character codes in URIs are NOT encoded, they are written in raw
# binary mode.
encoding = "utf-8"

class PropertyList(xml.sax.handler.ContentHandler):
    """
    Parses an Apple iTunes Music Library.xml file into a
    dictionary.
    """
    
    def __init__(self, file = None):
        # Root object
        self.plist = None
        # Names of parent elements
        self.parents = [None]
        # Dicts can be nested
        self.dicts = []
        # So can arrays
        self.arrays = []
        # Since dicts can be nested, we have to keep a queue of the
        # current outstanding keys whose values we have yet to set.
        self.keys = []
        # Accumulated CDATA
        self.cdata = ""

        # Open file
        if type(file) == str:
            file = open(file, 'r')

        # Parse it
        parser = xml.sax.make_parser()
        parser.setContentHandler(self)
        parser.parse(file)

    def __str__(self):
        return pprint.pformat(self.plist)

    def __getitem__(self, name):
        if type(self.plist) == dict:
            return self.plist[name]
        else:
            return self.plist

    def startElement(self, name, attrs):
        if name == "dict":
            self.dicts.append({})
        elif name == "array":
            self.arrays.append([])
        else:
            self.cdata = ""

        self.parents.append(name)

    def endElement(self, name):
        last = self.parents.pop()
        assert last == name

        value = None

        if name == "dict":
            value = self.dicts.pop()
        elif name == "key":
            if self.keys and self.keys[-1] == "Tracks":
                # Convert track keys to integer
                self.keys.append(int(self.cdata.strip()))
            else:
                self.keys.append(self.cdata.strip())
        elif name == "array":
            value = self.arrays.pop()
        elif name == "data":
            # Contents interpreted as Base-64 encoded
            value = base64.b64decode(self.cdata.strip())
        elif name == "date":
            # Contents should conform to a subset of ISO 8601 (in
            # particular, YYYY '-' MM '-' DD 'T' HH ':' MM ':' SS 'Z'.
            # Smaller units may be omitted with a loss of precision)
            year = month = day = hour = minutes = seconds = 0
            try:
                (date, time) = self.cdata.strip().split('T')
                parts = date.split('-')
                if len(parts) >= 1:
                    year = int(parts[0])
                    if len(parts) >= 2:
                        month = int(parts[1])
                        if len(parts) >= 3:
                            day = int(parts[2])
                time = time.replace('Z', '')
                parts = time.split(':')
                if len(parts) >= 1:
                    hour = int(parts[0])
                    if len(parts) >= 2:
                        minutes = int(parts[1])
                        if len(parts) >= 3:
                            seconds = int(parts[2])
            except:
                pass
            value = datetime.datetime(year, month, day, hour, minutes, seconds)
        elif name == "real":
            # Contents should represent a floating point number
            # matching ("+" | "-")? d+ ("."d*)? ("E" ("+" | "-") d+)?
            # where d is a digit 0-9.
            value = float(self.cdata.strip())
        elif name == "integer":
            # Contents should represent a (possibly signed) integer
            # number in base 10
            value = int(self.cdata.strip())
        elif name == "string":
            value = self.cdata.strip()
        elif name == "true":
            # Boolean constant true
            value = True
        elif name == "false":
            # Boolean constant false
            value = False

        if self.parents[-1] == "plist":
            self.plist = value
        elif self.parents[-1] == "dict" and name != "key":
            if self.dicts and self.keys:
                key = self.keys.pop()
                self.dicts[-1][key] = value
        elif self.parents[-1] == "array":
            if self.arrays:
                self.arrays[-1].append(value)

    def characters(self, content):
        self.cdata += content

def writeurl(s, fileobj, encoding = "utf-8"):
    """
    Write a URI to the specified file object using the specified
    encoding. Escaped 8-bit character codes in URIs are NOT encoded,
    they are written in raw binary mode.
    """

    skip = 0
    for i, c in enumerate(s):
        if skip:
            skip -= 1
            continue
        if c == '%':
            # Write 8-bit ASCII character codes in raw binary mode
            try:
                a = array.array('B', [int(s[i+1:i+3], 16)])
                a.tofile(fileobj)
                skip = 2
                continue
            except IndexError:
                pass
            except ValueError:
                pass
        # Write everything else in the specified encoding
        fileobj.write(c.encode(encoding))

def usage():
    print """
Usage: %s [OPTION]... [FILE]

Options:

-e, --encoding=ENCODING  Use specified encoding for track and file names (default: %s)
-d, --directory=DIR      Replace path to Music Library with specified path
-h, --help               This message
""".lstrip() % (sys.argv[0], encoding)
    sys.exit(1)

def main():
    global encoding
    directory = None

    if len(sys.argv) < 1:
        usage()

    try:
        (opts, argv) = getopt.getopt(sys.argv[1:], "e:d:h", ["encoding=", "directory=", "help"])
    except getopt.GetoptError, e:
        print "Error: " + e.msg
        usage()

    for (opt, optval) in opts:
        if opt == "-e" or opt == "--encoding":
            encoding = optval
        if opt == "-d" or opt == "--directory":
            directory = optval
        else:
            usage()

    print "Parsing " + argv[0] + "...",
    sys.stdout.flush()
    plist = PropertyList(argv[0])
    print "done"

    (scheme, netloc, music_folder_path, params, query, fragment) = \
             urlparse.urlparse(plist['Music Folder'])

    for playlist in plist['Playlists']:
        if not playlist.has_key('Playlist Items'):
            continue

        try:
            filename = playlist['Name'] + ".m3u"
            m3u = open(filename, mode = "wb")
            m3u.write("#EXTM3U" + os.linesep)
        except:
            # Try to continue
            continue

        tracks = 0
        for item in playlist['Playlist Items']:
            try:
                track = plist['Tracks'][item['Track ID']]
                seconds = track['Total Time'] / 1000
                m3u.write("#EXTINF:" + "%d" % seconds + ",")
                m3u.write(track['Name'].encode(encoding))
                m3u.write(os.linesep)
                (scheme, netloc, path, params, query, fragment) = \
                         urlparse.urlparse(track['Location'])
                if directory is not None:
                    path = path.replace(music_folder_path, directory)
                writeurl(path, m3u, encoding)
                m3u.write(os.linesep)

                tracks += 1
                print filename + ": %d tracks\r" % tracks,
            except:
                # Try to continue
                continue

        print

        m3u.close()

if __name__ == "__main__":
    main()
