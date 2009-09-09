#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Create ``.pls`` playlists from music filenames.

Specify a path to be recursively searched for music files.

According to an `unofficial PLS format specification`__, the
``NumberOfEntries`` attribute can be placed *after* all
entries.  This allows for iterating through filenames without
keeping details for each entry in memory.

:Copyright: 2007 Jochen Kupperschmidt
:Date: 09-Feb-2007
:License: MIT

__ http://forums.winamp.com/showthread.php?threadid=65772
http://www.google.com/search?hl=en&q=python+pls+playlist&btnG=Search
python pls playlist - Google Search
http://homework.nwsnet.de/products/1a02_create-pls-playlists
Snippet: Create PLS playlists // homework prod.
"""

from itertools import ifilter
import os.path
import re
from sys import argv, exit, stdout


PATTERN = re.compile('\.(mp3|ogg)$', re.I)

def find_files(path):
    """Return all matching files beneath the path."""
    for root, dirs, files in os.walk(os.path.abspath(path)):
        for fn in ifilter(PATTERN.search, files):
            yield os.path.join(root, fn)

def create_playlist(filenames):
    """Create a PLS playlist from filenames."""
    yield '[playlist]\n\n'
    num = 0

    entry = (
        'File%d=%s\n'
        'Title%d=%s\n'
        'Length%d=-1\n\n')
    for filename in filenames:
        num += 1
        title = os.path.splitext(os.path.basename(filename))[0]
        yield entry % (num, filename, num, title, num)

    yield (
        'NumberOfEntries=%d\n'
        'Version=2\n') % num

if __name__ == '__main__':
    if len(argv) != 2:
        exit('Usage: %s <path to music files>'
            % os.path.basename(argv[0]))

    filenames = find_files(argv[1])
    map(stdout.write, create_playlist(filenames))

