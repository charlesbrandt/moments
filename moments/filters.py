#!/usr/bin/env python
# -*- coding: latin-1 -*-
# ----------------------------------------------------------------------------
# moments
# Copyright (c) 2009-2011, Charles Brandt
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# ----------------------------------------------------------------------------
"""
functions useful for extracting moments from a group of log files
based on the tags we want to extract

"""
import os, re
import unicodedata, sys

from moments.journal import Journal
from moments.path import Path, check_ignore, load_journal
from moments.timestamp import Timestamp

def omit_date_tags(items):
    """
    take a list of tags
    leave out any that are a timestamp
    """
    new_list = []
    months = [ "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12" ] 
    for item in items:
        try:
            t = Timestamp(item)
        except:
            if not item in months:
                new_list.append(item)
    return new_list

def filter_list(items, ignores, search=False):
    """
    IF SEARCH IS NOT TRUE, IGNORES MUST BE AN EXACT MATCH
    
    take a list of items
    take a list of itmes to ignore
    return a new list of items based on first, original, with ignores removed
    """
    for i in ignores:
        if i in items:
            items.remove(i)
        elif search:
            for item in items:
                if re.search(i, item):
                    items.remove(item)
        else:
            #must not match
            pass
    return items

def filter_entries(journal, updates):
    """
    apply filters to the journal's entries in place
    #normalize/filter all of the data first...
    #as the system changes, so do the paths

    adapted from medialist.from_journal

    could consider adding this as a method to entry or data
    """
    for e in journal:
        filtered_data = ''
        for line in e.data.splitlines():
            if line:
                #for url quoted items??
                #item = urllib.unquote(item)

                [line] = find_and_replace( [line], updates)
                if line:
                    filtered_data += line + '\n'

        e.data = filtered_data
        #new_entries.append(e)


def filter_log(path, filters, save=False):
    """
    """
    if not os.path.isfile(path):
        raise ValueError, "path must be a file, got: %s" % path

    #j = Journal()
    #j.load(path)
    j = load_journal(path)
    
    j.filter_entries(filters)
    if save:
        #when it's time to save:
        j.save(path)


def filter_logs(path, updates=[], save=False):
    """
    walk the path, looking for moment logs
    for each log
    scan entries
    for each entry
    apply filter
    """
    
    add_tags = []
    ignore_dirs = [ ]
    log_check = re.compile('.*\.txt$')
    if os.path.isdir(path):
        for root,dirs,files in os.walk(path):
            for f in files:
                if not log_check.search(f):
                    continue
                
                cur_file = os.path.join(root, f)
                if not check_ignore(cur_file, ignore_dirs):
                    filter_log(cur_file, updates, save)
                        
    elif os.path.isfile(path) and log_check.search(path):
        filter_log(path, updates, save)
    else:
        #no logs to scan
        print "Unknown filetype sent as path: %s" % path

    print "finished filtering"

def remove_dupes(items):
    """
    make sure no item appears twice in list
    i.e. filter for any duplicates
    """
    clean = []
    for i in items:
        if not i in clean:
            clean.append(i)
    return clean

def union(set1, set2):
    """
    take two lists
    union the items in them
    """
    combined = set1[:]
    count = 0 
    for i in set2:
        if not i in combined:
            combined.append(i)
        else:
            count += 1
    print "Found: %s dupes" % count
    return combined

def intersect(set1, set2):
    """
    take two lists
    intersect the items in them
    """
    both = []
    for i in set1:
        if i in set2:
            both.append(i)
    return both

def difference(set1, set2):
    """
    take two lists
    return the differences

    NOTE THAT ORDER MATTERS!
    if 1 is a superset of 2, there will be a difference
    but if 2 is a superset of 1, there won't be a difference

    i.e.
    larger set first!
    larger = set1, smaller = set2
    """
    diff = []
    for i in set1:
        if not i in set2:
            diff.append(i)
    return diff

def intersect_journal_entries_with_tags(journal, tag_list):
    """
    look for all entries in the journal that have all tags in tag_list
    """
    entry_set = set()
    for tag in tag_list:
        if journal.tag(tag):
            if not entry_set:
                #must be our first one:
                entry_set = set(journal.tag(tag))
            else:
                #            time_set.intersect(set(l))
                entry_set = entry_set.intersection(set(journal.tag(tag)))
    return list(entry_set)

def union_journal_entries_with_tags(journal, tag_list):
    """
    look for all entries in the journal that have any tags in tag_list
    """
    entry_set = set()
    for tag in tag_list:
        if journal.tags(tag):
            entry_set = entry_set.union(set(journal.tag(tag)))
    return list(entry_set)

def union_journals(journal, other):
    """
    take another journal
    combine all entries in it and journal

    similar to merge_logs
    (to be consistent with intersect and difference behavior:
    return a new Journal with those entries)

    this is also what from_entries does
    """
    journal.from_entries(other)

def intersect_journals(journal, other):
    """
    take another journal,
    return a new journal
    with only the entries that are in common to both
    """
    common = []
    for entry in other:
        entry_time = str(entry.created)
        matched = False
        if journal.dates.has_key(entry_time):
            options = journal.dates[entry_time]
        else:
            options = []
        for existing in options:
            if existing.is_equal(entry):
                common.append(existing)
    return Journal(items=common)

def difference_journals(journal, other):
    """
    take another journal,
    return a new journal
    with the entries that are only in the other journal
    not in ourself

    NOTE:
    we may have entries in journal that are not in other...
    those will not be returned.
    this can be called in the opposite direction if those are wanted
    """
    diffs = []
    for entry in other:
        entry_time = str(entry.created)
        matched = False
        if journal.dates.has_key(entry_time):
            options = journal.dates[entry_time]
        else:
            options = []
        for existing in options:
            if existing.is_equal(entry):
                matched = True
        if not matched:
            diffs.append(entry)
    return Journal(items=diffs)


#UNTESTED BELOW HERE:

def flatten(journal, filename=None):
    """
    create a flat version of the journal without timestamps (or tags?)
    """
    if filename:
        f = codecs.open(filename, 'w', encoding='utf-8')
    elif journal.path:
        f = codecs.open(journal.path, 'w', encoding='utf-8')
    else:
        print "No path to save file to"
        exit()

    flat = ''
    for e in journal:
        flat += e.render_data()

    f.write(flat)
    f.close()

def flatten_first_lines(journal, separator=' '):
    """
    only keep the first line of each journal entry
    useful for playlists
    """
    flat = ''
    for e in journal:
        flat += e.data.splitlines()[0] + separator

    return flat

# not to be confused with association.filter_list
def find_and_replace(items, updates):
    """
    aka find_and_replace
    
    apply all updates in updates list 
    to all items in items list

    updates consist of a list of lists
    where the sub lists contain:
    (search_string, replace_string)
    """
    for u in updates:
        search_string = u[0]
        replace_string = u[1]
        #print search_string
        pattern = re.compile(search_string)
        for item in items:
            if pattern.search(item):
                index = items.index(item)
                items.remove(item)
                #print "ORIGINAL ITEM: %s" % item

                item = pattern.sub(replace_string, item)
                # not sure if python replace is faster than re.sub:
                #journal.replace(pu[0], pu[1])
                
                #print "     NEW ITEM: %s" % item
                items.insert(index, item)

    return items

class ExtractConfig(object):
    """
    used in /c/mindstream/moments-scripts/extract.py
    """
    def __init__(self):
        self.sources = ''
        self.ignores = ''
        self.extractions = []
        self.name = ''

def extract(journal, tag_list, etype="intersect"):
    """
    remove any entries tagged with a/all tag in tag_list

    saving journal (with missing entries) left to caller (if desired)
    """

    entries = []
    if etype == "union":
        entries = union_journal_entries_with_tags(journal, tag_list)
    elif etype == "intersect":
        entries = intersect_journal_entries_with_tags(journal, tag_list)
    else:
        print "Unknown type of extraction!!!"

    #sending fname creates place holder entries in the journal
    #not sure if we still need to do that [2008.11.04 16:58]
    #(dir, fname) = os.path.split(ofile)
    #journal.remove_many(entries, fname)
    journal.remove_many(entries)

    #rather than save here, lets just return the list of entries
    #then they can be added to another journal instance
    #or written directly to log by caller as they were here.
    return entries

def extract_many(path, extractions, ignores=[], save=False, extract_type="intersect"):
    """
    rather than go through all files for every extraction
    it is nice to go through all extractions during each file

    save extractions for each file
    rather than accumulating until end

    will make it trickier for trial runs
    can print actions or make temp logs
    """
    these_tags = []
    filename_tags = Path(path).to_tags()
    #print filename_tags
    filename_tags = filter_list(filename_tags, ignores, search=True)
    #print filename_tags
    filename_tags = omit_date_tags(filename_tags)
    these_tags.extend(filename_tags)

    if not os.path.isfile(path):
        raise ValueError, "path must be a file, got: %s" % path
    j = Journal()
    
    #j.load(path, add_tags=these_tags)
    #can add tags to the export, but don't want to add them in here:
    has_entries = j.load(path)
    for (tags, destination) in extractions:
        entries = extract(j, tags, extract_type)
        if len(entries):
            print "found %s entries with tag: %s in: %s" % (len(entries), tags, path)
            entries.reverse()
            j2 = Journal()
            j2.load(destination)
            for e in entries:
                e.tags.extend(these_tags)
                j2.update(e, 0)
                entry = e.render()
                e_ascii = entry.translate(unaccented_map()).encode("ascii", "ignore")
                print "adding entry to: %s\n%s" % (destination, e_ascii)
            if save:
                #this way we're saving any entries we extract to the new
                #destination before we save the original source file
                #
                #if there are permission problems writing the source file
                #at worst we'll have 2 copies of the same entry
                # (and that can be filtered out later)
                j2.save(destination)

    # do *not* want to save if the file passed to the journal did not get parsed as having entries
    # this would result in a blank file being saved,
    # resulting in data loss, if the text file was not in a moments format
    # i.e. check both if save is desired ('save' variable)
    # and if journal had entries ('has_entries' variable)
    if save and has_entries:
        #when it's time to save:
        j.save(path)

def extract_tags(path, extractions=[], ignores=[], save=False,
                 extract_type='intersect'):
    """
    accept a list of extractions
    where each extraction consists of a set of tags to look for
    (using extract_type)
    and a destination where matching entries should be extracted to

    ignores is a list of tags to leave out of the found entries
    (good for filtering tags generated from the original file path)
    
    this duplicates the logic for scanning all files from extract_tag
    it feels more readable to separate the two

    *2009.08.29 13:20:46
    now part of the moments module itself

    not to be confused with the Journal.extract method
    these functions are higher level operations that utilize Journal.extract

    also:
    # take a list of tags,
    # and the directory or file that you want to use as the source of the tags
    # go through all files, and remove those tags
    # saving them in a new separate file (or specified existing file)

    # adapted from pose.controllers.tags.extract
    
    """
    
    add_tags = []
    ignore_dirs = [ 'downloads', 'binaries' ]
    log_check = re.compile('.*\.txt$')
    if os.path.isdir(path):
        for root,dirs,files in os.walk(path):
            for f in files:
                if not log_check.search(f):
                    continue
                
                cur_file = os.path.join(root, f)
                if not check_ignore(cur_file, ignore_dirs):
                    extract_many(cur_file, extractions, ignores, save,
                                 extract_type)
                        
    elif os.path.isfile(path) and log_check.search(path):
        extract_many(path, extractions, ignores, save, extract_type)
    else:
        #no logs to scan
        print "Unknown filetype sent as path: %s" % path

    #print "finished extracting multiple tags to multiple destinations"


# use a dynamically populated translation dictionary to remove accents
# from a string
#
# http://effbot.python-hosting.com/file/stuff/sandbox/text/unaccent.py
# http://www.crummy.com/cgi-bin/msm/map.cgi/ASCII%2C+Dammit
# http://www.peterbe.com/plog/unicode-to-ascii
# see also phraseUnicode2ASCII()

# Translation dictionary.  Translation entries are added to this
# dictionary as needed.
##
CHAR_REPLACEMENT = {
    # latin-1 characters that don't have a unicode decomposition
    0xc6: u"AE", # LATIN CAPITAL LETTER AE
    0xd0: u"D",  # LATIN CAPITAL LETTER ETH
    0xd8: u"OE", # LATIN CAPITAL LETTER O WITH STROKE
    0xde: u"Th", # LATIN CAPITAL LETTER THORN
    0xdf: u"ss", # LATIN SMALL LETTER SHARP S
    0xe6: u"ae", # LATIN SMALL LETTER AE
    0xf0: u"d",  # LATIN SMALL LETTER ETH
    0xf8: u"oe", # LATIN SMALL LETTER O WITH STROKE
    0xfe: u"th", # LATIN SMALL LETTER THORN
    }


class unaccented_map(dict):
    """
    Maps a unicode character code (the key) to a replacement code
    (either a character code or a unicode string).
    """
    
    def mapchar(self, key):
        ch = self.get(key)
        if ch is not None:
            return ch
        de = unicodedata.decomposition(unichr(key))
        if de:
            try:
                ch = int(de.split(None, 1)[0], 16)
            except (IndexError, ValueError):
                ch = key
        else:
            ch = CHAR_REPLACEMENT.get(key, key)
        self[key] = ch
        return ch

    if sys.version >= "2.5":
        # use __missing__ where available
        __missing__ = mapchar
    else:
        # otherwise, use standard __getitem__ hook (this is slower,
        # since it's called for each character)
        __getitem__ = mapchar


def to_ascii(source):
    #print type(source)
    #source = source.translate(unaccented_map()).encode("ascii", "ignore")
    source = source.translate(unaccented_map())
    return source

def to_unicode(source):
    s = u''
    for c in source:
        try:
            s += unicode(c)
        except:
            pass
    return s

def to_ascii2(source):
    s = to_unicode(source)
    s = to_ascii(s)
    return s


def test_ascii():

    text = u"""

    "Jo, når'n da ha gått ett stôck te, så kommer'n te e å,
    å i åa ä e ö."
    "Vasa", sa'n.
    "Å i åa ä e ö", sa ja.
    "Men va i all ti ä dä ni säjer, a, o?", sa'n.
    "D'ä e å, vett ja", skrek ja, för ja ble rasen, "å i åa
    ä e ö, hörer han lite, d'ä e å, å i åa ä e ö."
    "A, o, ö", sa'n å dämmä geck'en.
    Jo, den va nôe te dum den.

    (taken from the short story "Dumt fôlk" in Gustaf Fröding's
    "Räggler å paschaser på våra mål tå en bonne" (1895).

    """

    print text.translate(unaccented_map())

    # note that non-letters are passed through as is; you can use
    # encode("ascii", "ignore") to get rid of them.  alternatively,
    # you can tweak the translation dictionary to return None for
    # characters >= "\x80".

    map = unaccented_map()

    print repr(u"12\xbd inch".translate(map))
    print repr(u"12\xbd inch".translate(map).encode("ascii", "ignore"))


def main():
    """
    *2011.08.30 09:09:19 
    imported from filter_logs
    that might not be the main functionality of this module
    """
    source = None
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            usage()
        source = sys.argv[1]

    updates = [ ['c\/media\/binaries', 'c/binaries'],
                ['^media\/', '/c/']
                ]
    filter_logs(source, updates, save=True)

if __name__ == '__main__':
    main()
