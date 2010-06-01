# ----------------------------------------------------------------------------
# moments
# Copyright (c) 2009-2010, Charles Brandt
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
Moments Journal object and functions related to using journals

A journal holds a collection of Moments (or Entries, if no timestamps)
"""
import re, codecs, os
from datetime import datetime

from log import Log
from moment import Moment
from timestamp import Timestamp
from association import Association, check_ignore
#from path import Path

# not to be confused with association.filter_list
def filter_items(items, updates):
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
                #self.replace(pu[0], pu[1])
                
                #print "     NEW ITEM: %s" % item
                items.insert(index, item)

    return items

def log_action(destination, message, tags=[]):
    """
    this is a common need...
    open a journal
    create a new entry (now)
    and save the journal/log

    this returns the entry created.
    """
    j = Journal()
    j.from_file(destination)
    entry = j.make_entry(message, tags)
    j.to_file()

    #print entry.render()
    return entry

class Journal(list):
    """
    Main Moments module for collecting Moment objects in one place

    Based on a standard python list
    """
    def __init__(self, path=None, items=[], title=''):
        list.__init__(self)
        #actual entries will be stored in self

        self.dates = Association()

        #keys must be tag name
        self.tags = Association()

        # used for default file path:
        # convert to string just incase a Path object is sent
        self.path = str(path)
        if path:
            self.from_file(self.path)
        elif items:
            self.from_entries(items)

        # renamed self.name to self.path
        # then use name as a general name for the journal, if displayed
        # *2009.11.07 10:28:44 
        # using title instead of name, then if anything else is still
        # using name the old way, it will flag a more recognizable error
        self.title = title

        #could generate a title based on path basename if path exists:

        
##     def __repr__(self, entries=False):
##         j = ''
##         j += "Journal with %s entries.\n" % (len(self))
##         if entries:
##             for e in self:
##                 j += e.render()
##         return j

    def as_text(self):
        j = ''
        j += "Journal with %s entries.\n" % (len(self))
        for e in self:
            j += e.render()
        return j
        
    def show_entries(self):
        print self.__repr__(entries=True)
    
    def to_file(self, filename=None, sort='original', include_path=False):
        """
        >>> from entry import Entry
        >>> e = Entry("test entry")
        >>> j.add_entry(e)
        >>> j.to_file("sample_log2.txt")
        >>> k = Journal()
        >>> k.from_file("sample_log2.txt")
        >>> len(k.entries)
        2
        """
        if filename:
            self.path = str(filename)

        if self.path:
            l = Log(self.path)
        else:
            print "No name to save Journal to"
            exit()

        #l.from_journal(self, holder, entry)
        l.from_entries(self.sort_entries(sort=sort), include_path=include_path)
        l.to_file()
        l.close()

    def sort_entries(self, sort='original'):
        """
        rearrange the order of the entries in the journal

        can specify order:

        'original'
        to keep the original order that the entries were added to the journal

        'reverse'

        'chronological' or 'oldest to newest'
        oldest entries first in the list

        'reverse-chronological'  or 'newest to oldest'
        
        if not all entries are wanted, see self.limit()
        """
        #print sort
        if sort == "original":            
            #could copy for pure list object:
            #return self[:]
            return self
        
        elif sort == "reverse":
            #*2010.04.16 12:49:15 
            #this 
            self.reverse()
            #could copy for pure list object:
            #return self[:]
            return self

        entry_times = self.dates.keys()

        if sort == "reverse-chronological" or sort == 'newest to oldest':
            entry_times.sort()
            entry_times.reverse()
        elif sort == "chronological" or sort == 'oldest to newest':
            print "oldest to newest"
            entry_times.sort()
        else:
            raise ValueError, "Unknown sort option supplied: %s" % sort
            
        entries = Journal()
        for et in entry_times:
            elist = self.dates[et]
            for entry in elist:
                entries.update_entry(entry)

        #now that journals can be load on create, don't want to pass path in
        #if we want an empty journal
        entries.path = self.path
        entries.title = self.title
        # *2009.11.07 12:19:14 
        # self is not updated to new version automatically
        # old order seems to persist
        # may want to try using value that is returned 
        #self = entries
        return entries

    def flatten(self, filename=None):
        """
        save without timestamps (or tags?)
        """
        if filename:
            f = codecs.open(filename, 'w', encoding='utf-8')
        elif self.path:
            f = codecs.open(self.path, 'w', encoding='utf-8')
        else:
            print "No path to save file to"
            exit()

        flat = ''
        for e in self:
            flat += e.render_data()

        f.write(flat)
        f.close()

    #formerly: add_log_to_journal, add_file
    def from_file(self, log_name=None, add_tags=[]):
        """
        adds a log file to the journal object currently in memory

        this can be called multiple times with different filenames
        to merge those files/entries into the journal

        >>> from journal import *
        >>> j = Journal()
        >>> j.from_file("sample_log.txt")
        >>> len(j.entries)
        1

        return True if the file was able to be loaded
        False if it was not a journal/Log file
        """
        found_entries = False

        if log_name:
            #if something is passed in, that will override the original path
            self.path = str(log_name)
        elif not self.path:
            #if our path wasn't originally initialized, go ahead and set it:
            self.path = Timestamp().filename()
        else:
            #no log_name sent, but self.path was set
            pass
        
        l = Log(self.path)
        l.from_file(self.path)

        #*2009.08.05 11:01:28 
        #since we are no longer using the dates as the primary way to index
        #entries in a journal, should be able to add entries w/o timestamps
        #entries = l.to_entries(add_tags, moments_only=True)
        entries = l.to_entries(add_tags)
        #print "%s entries loaded from file" % len(entries)
        #print "%s entries in self before merging in entries" % len(self)
        self.from_entries(entries)
        #print "%s entries in self after merging in entries" % len(self)

        if l.has_entries:
            found_entries = l.has_entries
        
        l.close()
        
        return found_entries

    #aka add_entries:
    def from_entries(self, entries):
        """
        loop over a list of entries to add/update each one to the journal
        """
        for e in entries:
            self.update_entry(e)
        
    def _add_entry(self, entry, position=None):
        """
        this is the base case for adding an entry
        adds the entry object to the journal's list of entries

        will add multiple copies of the same entry to the journal
        use update_entry to avoid duplicates
        """
        if position is None:
            #cannot assume insert here... will reverse the list on log read
            self.append(entry)
        else:
            self.insert(position, entry)

        if hasattr(entry, "created"):
            entry_time = str(entry.created)
            self.dates.associate(entry, entry_time)

        for t in entry.tags:
            self.tags.associate(entry, t)

    def replace_entry(self, entry):
        """
        remove all entries from the journal with the same timestamp as
        entry
        then add the new entry to the journal

        i.e.
        accepts a new entry
        and uses it to find and then remove the original one(s)
        add the new one to the journal
        thereby replacing the original(s)
        """
        entry_time = str(entry.created)

        if self.dates.has_key(entry_time):
            options = self.dates[entry_time]
        else:
            options = []
        for existing in options:
            self.remove_entry(existing)

        self._add_entry(entry)

    def make_entry(self, data, tags=[], created=None, position=0):
        """
        helper for making a new entry right in a journal object
        this way should not need to import moments.entry.Entry items elsewhere
        """
        if not created:
            created = datetime.now()
        entry = Moment(data, tags, created)
        self.update_entry(entry, position=position)
        return entry
        
    def update_entry(self, entry, position=None):
        """
        checks if an entry already exists in the journal
        if other entries in with that time stamp are similar, 
        see if they can be merged easily (i.e. only tags differ)

        otherwise just add it as a separate entry
        no longer attempting to choose which one to keep here
        since journal can hold multiple entries with the same timestamp

        can merge later as needed using dedicated script for that purpose
        """
        if entry not in self:
            if not hasattr(entry, "created"):
                self._add_entry(entry, position)
                
            else:
                entry_time = str(entry.created)

                #print "Adding Entry: %s" % entry_time
                if not self.dates.has_key(entry_time):
                    self._add_entry(entry, position)

                elif self.dates.has_key(entry_time):
                    #it must have *something* in that time slot
                    #check for duplicates
                    options = self.dates[entry_time]
                    found_match = False
                    for existing in options:
                        #if ( (existing.data == entry.data) and
                        #       (existing.tags == entry.tags) ):
                        if existing.is_equal(entry):
                            #print "DUPE, but tags and data are same... skipping"
                            
                            found_match = True
                        elif existing.data == entry.data:
                            #tags must differ... those are easy to merge:
                            print "only TAGS differ"
                            print "original: %s" % existing.tags
                            print "new: %s" % entry.tags
                            existing.tags.union(entry.tags)
                            print "merged: %s" % existing.tags
                            found_match = True
                        else:
                            #this one didn't match
                            #but we won't add the entry until we've checked them all
                            pass
                    if not found_match:
                        #2009.12.04 16:03:15 
                        #this information doesn't help much anymore:
                        #print "MULTIPLE ENTRIES EXISTS AT: %s" % (entry_time)
                        #print "but none matched this one.  Adding now"
                        self._add_entry(entry, position)
        else:
            print "Entry (%s) already exists in journal" % entry_time

    def remove_entry(self, entry):
        """
        for each entry
          scan through all tags to see if they reference that entry,
          if they do, remove the reference
          then remove the entry from the journal.

        """
        #text_time = str(entry.created)
        #text_time = e.created.strftime(time_format)

        self.tags.remove(entry)
        self.dates.remove(entry)

        #remove from the list of entries
        self.remove(entry)

    def remove_entries(self, entries):
        """
        take a list of entry objects,
        remove each one
        """
        for e in entries:
            self.remove_entry(e)

    def limit(self, start, end=None):
        """
        take a start and end time
        return all entries in the journal that fall in that range

        
        """
        now = datetime.now()
        if not end:
            end = now

        #checking for datetime passed in... convert to Timestamp
        if type(start) == type(now):
            start = Timestamp(start)
        if type(end) == type(now):
            end = Timestamp(end)
            
        times = self.dates.keys()
        times.sort()

        matches = []
        for t in times:
            #not sure why we're using just time here
            #seems like we would want to use the date too?
            #pytime = Timestamp(t).time
            pytime = Timestamp(t).datetime
            if (pytime >= start.datetime) and (pytime <= end.datetime):
                matches.extend(self.dates[t])
        return matches

    def intersect_tags(self, tag_list):
        entry_set = set()
        for tag in tag_list:
            if self.tags.has_key(tag):
                if not entry_set:
                    #must be our first one:
                    entry_set = set(self.tags[tag])
                else:
                    #            time_set.intersect(set(l))
                    entry_set = entry_set.intersection(set(self.tags[tag]))
        return list(entry_set)


    def union_tags(self, tag_list):
        entry_set = set()
        for tag in tag_list:
            if self.tags.has_key(tag):
                entry_set = entry_set.union(set(self.tags[tag]))
        return list(entry_set)

    def union(self, other):
        """
        take another journal
        combine all entries in it and self

        similar to merge_logs
        (to be consistent with intersect and difference behavior:
        return a new Journal with those entries)

        this is also what from_entries does
        """
        self.from_entries(other)

    def intersect(self, other):
        """
        take another journal,
        return a new journal
        with only the entries that are in common to both
        """
        common = []
        for entry in other:
            entry_time = str(entry.created)
            matched = False
            if self.dates.has_key(entry_time):
                options = self.dates[entry_time]
            else:
                options = []
            for existing in options:
                if existing.is_equal(entry):
                    common.append(existing)
        return Journal(items=common)

    def difference(self, other):
        """
        take another journal,
        return a new journal
        with only the entries that are only in the other journal
        not in ourself

        NOTE:
        we may have entries in self that are not in other...
        those will not be returned.
        this can be called in the opposite direction if those are wanted
        """
        diffs = []
        for entry in other:
            entry_time = str(entry.created)
            matched = False
            if self.dates.has_key(entry_time):
                options = self.dates[entry_time]
            else:
                options = []
            for existing in options:
                if existing.is_equal(entry):
                    matched = True
            if not matched:
                diffs.append(entry)
        return Journal(items=diffs)
        
#UNTESTED BELOW HERE:

    def filter_entries(self, updates):
        """
        apply filters to the journal's entries in place
        #normalize/filter all of the data first...
        #as the system changes, so do the paths

        adapted from medialist.from_journal

        could consider adding this as a method to entry or data
        """
        for e in self:
            filtered_data = ''
            for line in e.data.splitlines():
                if line:
                    #for url quoted items??
                    #item = urllib.unquote(item)
                    
                    [line] = filter_items( [line], updates)
                    if line:
                        filtered_data += line + '\n'
                        
            e.data = filtered_data
            #new_entries.append(e)


    def extract(self, tag_list, etype="intersect"):
        """
        saving journal (with missing entries) left to caller (if desired)
        """
        
        entries = []
        if etype == "union":
            entries = self.union_tags(tag_list)
        elif etype == "intersect":
            entries = self.intersect_tags(tag_list)
        else:
            print "Unknown type of extraction!!!"

        #sending fname creates place holder entries in the journal
        #not sure if we still need to do that [2008.11.04 16:58]
        #(dir, fname) = os.path.split(ofile)
        #self.remove_entries(entries, fname)
        self.remove_entries(entries)

        #rather than save here, lets just return the list of entries
        #then they can be added to another journal instance
        #or written directly to log by caller as they were here.
        return entries

    def associate_data(self):
        """
        add a new property to the Journal: datas
        at one point this was generated automaticaly,
        but that slowed things down

        this allows it to be generated when it is needed
        which so far is only when then node.directory object
        is looking for a default image
        """
        self.datas = Association()
        for entry in self:
            self.datas.associate(entry, entry.data)

    def associate_files(self):
        """
        add a new property to the Journal: files
        similar to associate_datas

        but checks each entry's data for path information
        if path is found
        just take the filename portion
        and associate the entry with that portion

        otherwise associate the whole data

        """
        self.files = Association()
        for entry in self:
            lines = entry.data.splitlines()
            for line in lines:
                if re.search('/', line):
                    name = os.path.basename(line)
                    self.files.associate(entry, name)
                elif line.strip():
                    self.files.associate(entry, line.strip())
                else:
                    #must be a blank line
                    pass
                
if __name__ == "__main__":
    import doctest
    doctest.testmod()
