"""
Moments Journal object and functions related to using journals
"""
import re, codecs, os
from datetime import datetime

from log import Log
from moment import Moment
from timestamp import Timestamp
from association import Association, check_ignore
from tags import path_to_tags

# not to be confused with association.filter_list
def filter_items(items, updates):
    """
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

def load_journal(path, add_tags=[]):
    """
    walk the given path and
    create a journal object from all logs encountered in the path
    
    create a temporary, in memory, journal from logs

    this works for both directories and log files

    *2009.06.18 12:38:45
    
    this was started to be abstracted from osbrowser in player.py.  
    By moving here, we minimize dependencies outside of Moments module

    load_journal cannot guarantee that the returned Journal item will have a
    filename (self.name) associated with it for later saving.

    in that case should use:
    ::
    
      j = Journal()
      j.from_file(path, add_tags=these_tags)

    -or-
    ::
    
      j = load_journal(path)
      j.name = destination

    """
    #ignore_dirs = [ 'downloads', 'binaries' ]
    ignore_dirs = [ 'downloads' ]
    j = Journal()
    log_check = re.compile('.*\.txt$')
    if os.path.isdir(path):
        for root,dirs,files in os.walk(path):
            for f in files:
                if not log_check.search(f):
                    continue

                if not check_ignore(os.path.join(root, f), ignore_dirs):
                    these_tags = add_tags[:]
                    #will need to abstract context_tags() too... move to Tags
                    filename_tags = path_to_tags(os.path.join(root, f))
                    these_tags.extend(filename_tags)
                    j.from_file(os.path.join(root, f), add_tags=these_tags)

    elif os.path.isfile(path) and log_check.search(path):
        j.from_file(path, add_tags)
    else:
        #no journal to create
        pass
    return j


class Journal(list):
    """
    Main Moments module for collecting Moment objects in one place

    Based on a standard python list
    """
    def __init__(self, name=None):
        list.__init__(self)
        #actual entries will be stored in self

        self.dates = Association()

        #keys must be tag name
        self.tags = Association()

        #used for default filename:
        self.name = name

    def __repr__(self, entries=False):
        j = ''
        j += "Journal with %s entries.\n" % (len(self))
        if entries:
            for e in self:
                j += e.render()
        return j
        
    def show_entries(self):
        print self.__repr__(entries=True)
        #this would also work:
        #entries = self.to_entries()
        #for e in entries:
        #    print e.render()
    
    def to_file(self, filename=None, sort='original'):
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
            l = Log(filename)
        elif self.name:
            l = Log(self.name)
        else:
            print "No name to save Journal to"
            exit()

        #l.from_journal(self, holder, entry)
        l.from_entries(self.to_entries(sort=sort))
        l.to_file()
        l.close()

    #*2009.08.09 05:19:35
    #may want to rename to sort_self
    #self is already a list of entries
    def to_entries(self, sort='original', all_placeholders=True):
        """
        return a list of entries the make up the current journal

        can specify order:

        'original'
        to keep the original order that the entries were added to the journal

        'chronological' or 'oldest to newest'
        oldest entries first in the list

        'reverse-chronological'  or 'newest to oldest'
        if not all entries are wanted, see self.limit()
        """
        if sort == "original":            
            #could copy for pure list object:
            #return self[:]
            return self
        
        elif sort == "reverse":
            self.reverse()
            #could copy for pure list object:
            #return self[:]
            return self

        entry_times = self.dates.keys()

        if sort == "reverse-chronological" or sort == 'newest to oldest':
            entry_times.sort()
            entry_times.reverse()
        elif sort == "chronological" or sort == 'oldest to newest':
            entry_times.sort()
        else:
            raise ValueError, "Unknown sort option supplied: %s" % sort
            
        entries = Journal()
        for et in entry_times:
            elist = self.dates[et]
            for entry in elist:
                entries.update_entry(entry)
                ## if entry not in entries:
                ##     entries.append(entry)
                ## else:
                ##     print "multiple instances of same entry found."
                ##     print "j.to_entries: %s" % entry.render()
        ## entries = []
        ## for et in entry_times:
        ##     elist = self.dates[et]
        ##     for entry in elist:
        ##         if entry not in entries:
        ##             entries.append(entry)
        ##         else:
        ##             print "multiple instances of same entry found."
        ##             print "j.to_entries: %s" % entry.render()
        self = entries
        return entries

    def flatten(self, filename=None):
        """
        save without timestamps (or tags?)
        """
        if filename:
            f = codecs.open(filename, 'w', encoding='utf-8')
        elif self.name:
            f = codecs.open(self.name, 'w', encoding='utf-8')
        else:
            print "No name to save file to"
            exit()

        entries = self.to_entries()
        flat = ''
        for e in entries:
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
        """
        if not log_name:
            log_name = Timestamp().filename()

        #if our name wasn't originally initialized, go ahead and set it:
        if not self.name:
            self.name = log_name

        l = Log(log_name)
        l.from_file(log_name)

        #*2009.08.05 11:01:28 
        #since we are no longer using the dates as the primary way to index
        #entries in a journal, should be able to add entries w/o timestamps
        #entries = l.to_entries(add_tags, moments_only=True)
        entries = l.to_entries(add_tags)
        #print "%s entries loaded from file" % len(entries)
        #print "%s entries in self before merging in entries" % len(self)
        self.from_entries(entries)
        #print "%s entries in self after merging in entries" % len(self)
        
        l.close()

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

    def make_entry(self, data, tags=[], created=None):
        """
        helper for making a new entry right in a journal object
        this way should not need to import moments.entry.Entry items elsewhere
        """
        if not created:
            created = datetime.now()
        entry = Moment(data, tags, created)
        self.update_entry(entry, position=0)
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
                        if ( (existing.data == entry.data) and
                               (existing.tags == entry.tags) ):
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
                        print "MULTIPLE ENTRIES EXISTS AT: %s" % (entry_time)
                        print "but none matched this one.  Adding now"
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
        if not end:
            end = datetime.now()
            
        times = self.dates.keys()
        times.sort()

        matches = []
        for t in times:
            pytime = Timestamp(t).time
            if (pytime >= start) and (pytime <= end):
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

    def make_graph(self):
        g = graph.Graph(self.name, self.j)
        g.make_links()
        g.write_graph2()

if __name__ == "__main__":
    import doctest
    doctest.testmod()
