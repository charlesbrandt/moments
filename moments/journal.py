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
Moments Journal object and functions related to using journals

A journal holds a collection of Moments
(and Entries, for moments with no timestamps)
"""
import re, codecs, os
import urllib, urllib2
from datetime import datetime

try:
    import simplejson as json
except:
    try:
        import json
    except:
        print "No json module found"
        exit()

from log import Log
from moment import Moment
from timestamp import Timestamp, Timerange
from association import Association

def log_action(destination, message, tags=[]):
    """
    this is a common need...
    open a journal
    create a new entry (now)
    and save the journal/log

    this returns the entry created.
    """
    j = Journal()
    j.load(destination)
    entry = j.make(message, tags)
    j.to_file()

    #print entry.render()
    return entry

class Journal(object):
    """
    Main Moments module for collecting Moment entries in one place

    *2011.06.26 13:50:20
    not sure that it even makes sense to base this on a standard list
    should use a list internally
    but we really don't use any of the methods for a list to interact
    with a Journal object

    so we could have
    self._entries
    self._tags
    self._dates

    to store everything internally
    and then use custom methods for interacting with the Journal
    these methods should be the same
    whether the Journal is a local, native, instance,
    or if it is remote.

    i.e.
    using journal object attributes directly in code is discouraged
    to ensure that local and remote journal objects work identically

    """
    def __init__(self, path=None, items=[], title=None, debug=False):

        self._entries = []

        #keys are compact date string
        self._dates = Association()

        #keys are tag name
        self._tags = Association()

        # renamed self.name to self.path
        # then use name as a general name for the journal, if displayed
        # *2009.11.07 10:28:44 
        # using title instead of name, then if anything else is still
        # using name the old way, it will flag a more recognizable error
        self.title = title
        
        self.debug = debug

        #*2011.06.26 13:45:20
        #really no such thing as a default path (self.path)
        # used for default file path:
        # convert to string just incase a Path object is sent
        #self.path = str(path)

        #if we want to store it to a path, then should specify that
        #in a to_file / save call
        #otherwise should keep track of all paths loaded
        #so that we can reload them later.
        self.loaded = []
        #or ...
        #could index based on original source too
        #this would allow them to be re-saved to their original source
        self._sources = Association()
        
        if path:
            self.load(path)

        if items:
            self.update_entries(items)





    #*2011.06.26 13:53:03
    #should there be a to_file
    #and also a to_original_files (or something like that) ?
    #could loop through all of self.loaded and store changes to those
    #entries affected in those sources

    #aka to_file
    def save(self, filename=None, order='original', include_path=False):
        """
        >>> from entry import Entry
        >>> e = Entry("test entry")
        >>> j.add_entry(e)
        >>> j.to_file("sample_log2.txt")
        >>> k = Journal()
        >>> k.load("sample_log2.txt")
        >>> len(k.entries)
        2
        """
        if filename:
            self.path = str(filename)

        if hasattr(self, "path") and self.path:
            l = Log(self.path)
        else:
            print "No name to save Journal to"
            exit()

        #l.from_journal(self, holder, entry)
        l.from_entries(self.sort(order=order), include_path=include_path)
        l.to_file()
        l.close()


    def save_originals(self):
        """
        loop through all self.sources or self.loaded
        and save the corresponding entries back
        (only if there is an actual change???)

        might want to return any entries that don't have a destination
        or would it be better to return an error?
        or not save if entries don't have a destination
        """
        pass

    def save_instance(self, instance_file):
        """
        save the currently loaded sources to an instance file
        """
        pass
    
    def load_instance(self, instance_name, instance_file):
        """
        load the first entry tagged instance_name from the instance file
        """
        pass
    
    #aka open, etc
    #formerly: from_file, add_log_to_journal, add_file
    def load(self, log_name, add_tags=[]):
        """
        adds a log file to the journal object currently in memory

        this can be called multiple times with different filenames
        to merge those files/entries into the journal

        >>> from journal import *
        >>> j = Journal()
        >>> j.load("sample_log.txt")
        >>> len(j.entries)
        1

        return True if the file was able to be loaded
        False if it was not a journal/Log file
        """
        found_entries = 0

        if not str(log_name) in self.loaded:
            self.loaded.append(str(log_name))
        #TODO:
        #should also handle adding entry to self._sources??
        #or will that happen in update_entries

        #would it be better for sources and loaded to be associated
        #on an update?
        #that way if entries are added outside of a load
        #the sources would still get updated.

            
        l = Log()
        l.from_file(str(log_name))

        entries = l.to_entries(add_tags)
        #print "%s entries loaded from file" % len(entries)
        #print "%s entries in self before merging in entries" % len(self)
        self.update_many(entries)
        #print "%s entries in self after merging in entries" % len(self)

        #if l.has_entries:
        found_entries = len(entries)
        
        l.close()
        
        return found_entries


    def reload(self):
        """
        create a new instance of a journal
        based on the paths we have previously loaded
        (self.loaded)

        load everything that was previously loaded
        then swap out the contents old journal for the new one
        """
        #use this to load new _entries, etc
        temp_j = Journal()
        for item in self.loaded:
            new_j.load(item)
            #temp_j = load_journal(item)
            #new_j.from_entries(temp_j.entries())
            #del temp_j
        old_entries = self._entries
        old_tags = self._tags
        old_dates = self._dates
        old_sources = self._sources
        
        self._entries = new_j._entries
        self._tags = new_j._tags
        self._dates = new_j._dates
        self._sources = new_j._sources

        del old_entries
        del old_tags
        del old_dates
        del old_sources


    def _add(self, entry, position=None):
        """
        this is the base case for adding an entry
        blindly adds the entry object to the journal's list of entries
        no checks are performed

        will add multiple copies of the same entry to the journal
        use update to avoid duplicates
        """
        if position is None:
            #cannot assume insert here...
            #insert(0, entry) reverses the list order on log read
            self._entries.append(entry)
        else:
            self._entries.insert(position, entry)

        if hasattr(entry, "created") and entry.created:
            entry_time = entry.created.compact()
            self._dates.associate(entry, entry_time)
        else:
            self._dates.associate(entry, None)

        for t in entry.tags:
            self._tags.associate(entry, t)

    #TODO:
    #integrate source
    def update(self, entry, position=None, source=None):
        """
        checks if an entry already exists in the journal
        if other entries in with that time stamp are similar, 
        see if they can be merged easily (i.e. only tags differ)

        otherwise just add it as a separate entry
        no longer attempting to choose which one to keep here
        since journal can hold multiple entries with the same timestamp

        can merge later as needed using dedicated script for that purpose
        """
        if not hasattr(entry, "created") or not entry.created:
            if entry not in self._entries:
                self._add(entry, position)
                if self.debug: print "Entry has no time associated, and no other entry found. added"

        else:
            #this makes entry_time available in the event the entry already
            #is in the journal:
            #print entry.created
            entry_time = entry.created.compact()
            if entry not in self._entries:

                if not self._dates.has_key(entry_time):
                    self._add(entry, position)
                    if self.debug: print "No other entry found with time: %s. added" % entry_time
                
                elif self._dates.has_key(entry_time):
                    #it must have *something* in that time slot
                    #check for duplicates
                    if self.debug: print "Other entries found with time: %s. checking all.." % entry_time

                    options = self._dates[entry_time]
                    found_match = False
                    for existing in options:

                        if existing.is_equal(entry, debug=self.debug):
                            #print "DUPE, but tags and data are same... skipping"
                            found_match = True
                            if self.debug: print "Equal entry found. Skipping"

                        #only want to merge if we have data
                        #otherwise blank entries can end up grouped together
                        elif entry.data and (existing.data == entry.data):
                            #tags must differ... those are easy to merge:
                            print "from: %s, %s" % (existing.path, existing.created)
                            print "and: %s, %s" % (entry.path, entry.created)
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
                        self._add(entry, position)

                        if self.debug: print "No equivalent entries found. adding"
            else:
                if self.debug: print "Entry (%s) already exists in journal" % entry_time

    #aka create, new
    def make(self, data, tags=[], created=None, source='', position=0):
        """
        helper for making a new entry right in a journal object
        this way should not need to import moments.entry.Entry elsewhere
        """
        if not created:
            created = datetime.now()
        entry = Moment(data, tags, created, path=source)
        #print "Journal.make.position: %s" % position
        self.update(entry, position=position)
        return entry

    #AKA DELETE
    def remove(self, entry):
        """
        remove associations from self._dates and self._tags
        then remove the entry from the journal.
        """
        #text_time = str(entry.created)
        #text_time = e.created.strftime(time_format)

        self._tags.remove(entry)
        self._dates.remove(entry)

        #remove from the list of entries
        self._entries.remove(entry)

    #*2011.07.09 10:32:42 
    #is this ever used?
    #seems dangerous to remove everything at a given timestamp
    #more likely to add as a separate one
    #or remove explicitly and then add/update/make
    ## def replace(self, entry):
    ##     """
    ##     remove all entries from the journal with the same timestamp as entry
    ##     then add the new entry to the journal

    ##     i.e.
    ##     accepts a new entry
    ##     and uses it to find and then remove the original one(s)
    ##     add the new one to the journal
    ##     thereby replacing the original(s)
    ##     """
    ##     entry_time = entry.created.compact()

    ##     if self._dates.has_key(entry_time):
    ##         options = self._dates[entry_time]
    ##     else:
    ##         options = []
    ##     for existing in options:
    ##         self.remove(existing)

    ##     self._add(entry)

    #aka from_entries
    #aka add_entries
    #aka update_entries
    def update_many(self, entries, source=None):
        """
        loop over a list of entries to add/update each one to the journal
        """
        for e in entries:
            self.update(e, source=source)

    #aka remove_entries
    def remove_many(self, entries):
        """
        take a list of entry objects,
        remove each one
        """
        for e in entries:
            self.remove(e)



    #Following are all different ways to READ
    #they are also closely related to the hidden properties:
    #_tags, _dates, _entries

    #*2011.07.05 21:14:47
    #thinking that it makes sense to have two separate calls
    #could combine tag and tags (etc)
    #by returning the plural version (dict) when no tag specified
    #but the function name is unclear in that case
    
    def tag(self, tag_key=None):
        """
        lookup tag_key in self._tags

        should only return a list of entries associated with that tag
        not a dict
        with the tag name
        server can do that
        but server needs to be a little different
        """
        #print self._tags.keys()
        if tag_key and self._tags.has_key(tag_key):
            #print self._tags[tag_key]
            ## moments = []
            ## for m in self._tags[tag_key]:
            ##     #instead of rendering a string:
            ##     #moments.append(m.render())
            ##     #supply a dictionary of the moment item
            ##     moments.append(m.as_dict())
            #return { tag_key:self._tags[tag_key] }
            return self._tags[tag_key]
        ## elif tag_key:
        ##     #must not have any content associated with this tag
        ##     return { tag_key:[] }
        else:
            #could also return self.tags()
            #return self.tags()
            #return { 'tags': self._tags.keys() }
            #return { tag_key:[] }
            return []

    def tags(self, tags=[]):
        """
        return a dictionary with:
        all tags as keys, and
        number of entries for each tag as values

        *2011.07.10 10:38:07
        also
        could use mindstream.entries_tagged
        to accept a list of tags
        and combine all of those entries into a single list
        and return that
        """
        if tags:
            #*2011.11.09 11:42:38
            #if there is only one tag
            #should we just call self.tag()???
            
            if not isinstance(tags, list):
                tags = [ tags ]
            found_entries = Journal()
            for t in tags:
                if self._tags.has_key(t):
                    #print len(self._tags[t])
                    found_entries.update_many(self._tags[t])

            found_entries = found_entries.sort("reverse-chronological")
            #return found_entries._entries
            return found_entries

        else:
            tdict = {}
            for tag in self._tags.keys():
                tdict[tag] = len(self._tags[tag])
            return tdict
    
    def date(self, date_key=None):
        """
        lookup date_key in self._dates
        date_key should be compact stamp
        """
        if date_key:
            if isinstance(date_key, Timestamp):
                ts = date_key
            else:
                ts = Timestamp(compact=date_key)

            #print ts, type(ts)
            #print ts.accuracy
            if ts.accuracy and ts.accuracy != "second":
                rr = Timerange(ts)
                #get the timerange
                tr = rr.default()
                #print tr
                #print tr.start.datetime
                #print tr.end.datetime
                entries = self.range(tr.start, tr.end)

                #return {ts.compact():entries}
                return entries
                
            elif self._dates.has_key(ts.compact()):
                entries = self._dates[ts.compact()]
                #print "LEN ENTRIES: %s" % len(entries)
                #print entries
                #return { ts.compact():entries }
                return entries
            else:
                #return { ts.compact():[] }
                return []
        else:
            #could also return self.dates()
            #return self.dates()
            #return { date_key:[] }
            return []
        

    def dates(self):
        """
        return a dictionary with:
        all dates as keys, and
        number of entries for each date as values
        """
        ddict = {}
        for key in self._dates.keys():
            #print "KEY:", key
            
            #key might be blank here (i.e. no timestamp)
            if key:
                ts = Timestamp(compact=key)
                #print ts
                ddict[ts.compact()] = len(self._dates[key])
            else:
                ddict[key] = len(self._dates[key])
        return ddict

    #aka item???
    def entry(self, index=None):
        """
        return the item at index point in list
        is this already defined on a list object? should be consistent
        """
        if len(self._entries) > index:
            return self._entries[index]
        else:
            return None

    def entries(self):
        """
        return a list of entries
        making a function call rather than an attribute
        to make consistent between local and remote calls
        """
        return self._entries
    
    def related(self, key):
        """
        look for tags
        if no matching tags
        see if it is a date string  (get range, find entries there)

        either way return tags that are related
        (maybe as a dictionary {'tag':number_of_items} ...
         same as self._tags)
        """
        #make sure we have it, otherwise nothing relates
        if not self._tags.has_key(key):
            return []
        
        entries = self._tags[key]
        related = []
        for e in entries:
            #todo:
            #could also generate a cloud
            #ranking most common related higher
            for t in e.tags:
                if t not in related:
                    related.append(t)

        return related
    
    def search(self, look_for, data=False, limit=0):
        """
        scan tags for tags matching (searching) look_for
        if data is True, look in entry.data too
        """
        tags = self._tags.keys()
        found = []

        # in this case, we'll return the whole entry
        if data:
            for e in self._entries:
                if re.search(look_for, e.data):
                    found.append(e)
                else:
                    for t in e.tags():
                        if re.search(look_for, t):
                            found.append(e)

        # in this case we'll only return matching tags
        else:
            results = []
            for t in tags:
                if re.search(look_for, t):
                    results.append(t)

            ## #now look for the results that start with "look_for"
            ## matches = []
            ## for r in results:
            ##     if re.match(look_for, r):
            ##         matches.append(r)
            ##         results.remove(r)

            # sort tags by the number of entries they have
            priority = []
            for tag in results:
                priority.append( (len(self._tags[tag]), tag) )
            priority.sort()
            priority.reverse()
            #print "Priority: %s" % priority
            
            for p in priority:
                found.append(p[1])

        if limit:
            found = found[:int(limit)]
            
        return found

    def sort(self, order='original'):
        """
        Sorts the items in our Journal's ._entries list
        
        returns a list of  the rearranged order of the entries in the journal

        can specify order:

        'original'
        to keep the original order that the entries were added to the journal

        'reverse'

        'chronological' or 'oldest to newest'
        oldest entries first in the list

        'reverse-chronological'  or 'newest to oldest'
        
        if not all entries are wanted, see self.range()
        """
        #print order
        if order == "original":            
            return self._entries
        
        elif order == "reverse":
            self._entries.reverse()
            return self._entries

        else:
            entry_times = self._dates.keys()

            if order == "reverse-chronological" or order == 'newest to oldest':
                entry_times.sort()
                entry_times.reverse()
            elif order == "chronological" or order == 'oldest to newest':
                if self.debug: print "oldest to newest"
                entry_times.sort()
                if self.debug: print entry_times
            else:
                raise ValueError, "Unknown sort option supplied: %s" % order

            entries = []
            for et in entry_times:
                elist = self._dates[et]
                for entry in elist:
                    entries.append(entry)

            assert len(entries) == len(self._entries)
            del self._entries
            self._entries = entries

            return entries

    #aka limit, timerange, mindstream.time_range
    def range(self, start=None, end=None):
        """
        if no start *and* end specified
        return the time range for the entries in the currently loaded journal

        if only start
        return the entries in range for the accuracy of the start (e.g. 1 day)

        if start and end
        return all entries in the journal that fall in that range

        should accept a string, a datetime object, or a Timestamp object
        """

        if start is None and end is None:
            dates = self._dates.keys()
            dates.sort()
            start = dates[0]
            end = dates[-1]
            #might have entries with no timestamp first:
            if start is None:
                start = dates[1]
            print start, end
            return Timerange(start=start, end=end)

        else:
            start = Timestamp(start)
            if end:
                end = Timestamp(end)
            else:
                relative = Timerange(start)
                end = relative.end

            times = self._dates.keys()
            times.sort()

            matches = []
            for t in times:
                #not sure why we're using just time here
                #seems like we would want to use the date too?
                #pytime = Timestamp(t).time

                #sometimes t is None... those don't fit in a range.
                if t:
                    pytime = Timestamp(t).datetime
                    if (pytime >= start.datetime) and (pytime <= end.datetime):
                        matches.extend(self._dates[t])
            return matches

    def clear(self):
        """
        clear mind
        start fresh

        in practice it's probably easier to just create a new journal
        but reload might need this
        """
        del self._entries
        self._entries = []
        del self._tags
        self._tags = Association()
        del self._dates
        self._dates = Association()
        
        self.loaded = []
        self.sources = Association()
        #todo
        #way to see how much memory is consumed by current process?
        #should show before and after if so

        return True

    def associate_data(self):
        """
        add a new property to the Journal: datas
        at one point this was generated automaticaly,
        but that slowed things down

        this allows it to be generated when it is needed
        which so far is only when then node.directory object
        is looking for a default image
        """
        self._datas = Association()
        for entry in self._entries:
            self._datas.associate(entry, entry.data)

    def associate_files(self):
        """
        add a new property to the Journal: files
        similar to associate_datas

        but checks each entry's data for path information
        if path is found
        just take the filename portion
        and associate the entry with that portion

        otherwise associate each line of the entry's data (as is)
        """
        self._files = Association()
        for entry in self._entries:
            lines = entry.data.splitlines()
            for line in lines:
                if re.search('/', line):
                    name = os.path.basename(line)
                    self._files.associate(entry, name)
                elif line.strip():
                    self._files.associate(entry, line.strip())
                else:
                    #must be a blank line
                    pass













class RemoteJournal(object):
    """
    This is a drop in replacement for Journal
    but rather than load and store the data in an internal data structure
    all information is retrieved from a journal_server using json

    ultimately this avoids needing to reload a large journal set
    when working on applications to leverage information in a journal.

    
    wraps calls to a journal_server to make the object interaction
    behave the same as a local Journal object

    Uses the following calls for GET and POST requests:
    
    POST:
    req = urllib2.urlopen(url, params)
    GET:
    req = urllib2.urlopen(url)
    
    """
    def __init__(self, source):
        #source should be the base url to connect to
        self.source = source

        #*2011.10.11 08:25:35 
        # I think something here is causing connections to be lost
        # over time less data is returned from moments server
        # restarting a server with a RemoteJournal instance fixes it
        
        #make sure we can handle cookies, if used in the future
        #self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        #self.opener = urllib2.build_opener(urllib2.HTTPHandler())
        #urllib2.install_opener(self.opener)
        
    def save(self, path=''):
        """
        call the save option on server
        """
        url = '%s/save/%s' % (self.source, path)
        req = urllib2.urlopen(url)
        return True

    def save_post(self, path=''):
        """
        call the save option on server
        using POST
        """
        values = { 'destination': path }
        params = urllib.urlencode(values)
        #url = '%s/save/%s' % (self.source, path)
        url = '%s/save' % (self.source)
        #POST:
        req = urllib2.urlopen(url, params)
        #json_raw = req.read()
        return True

    def load(self, path=''):
        """
        call the load option on server
        """
        url = '%s/load/%s' % (self.source, path)
        req = urllib2.urlopen(url)
        return True

    def load_post(self, path=''):
        """
        call the load option on server
        using POST
        """
        values = { 'source': path }
        params = urllib.urlencode(values)
        #url = '%s/load/%s' % (self.source, path)
        url = '%s/load' % (self.source)
        #POST:
        req = urllib2.urlopen(url, params)
        #json_raw = req.read()
        return True

    def update(self, entry, source=None, position=0):
        """
        with a remote journal, we can't really have an update..
        it's just a make behind the scenes
        so we'll call that
        """
        if source is None:
            source = entry.source

        if entry.created:
            created = entry.created.compact()
        else:
            created = entry.created
            
        self.make(data=entry.data, tags=entry.tags, created=created, source=source, position=position)
        
    def make(self, data, tags=[], created='', source='', position=0):
        values = { 'data' : data,
                   'tags' : tags,
                   'created' : created,
                   'source' : source,
                   'position' : position,
                   }
        print values
        params = urllib.urlencode(values)
        print params
        #url = '%s/load/%s' % (self.source, path)
        url = '%s/make' % (self.source)
        print url
        #POST:
        req = urllib2.urlopen(url, params)

    def remove(self, entry):
        values = { 'data' : entry.data,
                   'tags' : entry.tags,
                   'created' : entry.created,
                   'source' : entry.source,
                   }
        params = urllib.urlencode(values)
        #print params
        url = '%s/remove' % (self.source)
        #POST:
        req = urllib2.urlopen(url, params)
        #for debugging:
        #print req.read()
        req.close()
        

    def tags(self, item=''):
        """
        returns a dictionary of tags (with count) if no item specified
        otherwise returns a list of moments for item specified
        """
        values = {}
        params = urllib.urlencode(values)
        url = '%s/tags/%s' % (self.source, item)
        #POST:
        #req = urllib2.urlopen(url, params)
        #GET:
        req = urllib2.urlopen(url)
        json_raw = req.read()
        req.close()
        result = json.loads(json_raw)
        if item:
            entries = []
            entry_strings = result[item]
            for e in entry_strings:
                log = Log()
                log.write(e)
                log_entries = log.to_entries()
                if len(log_entries) > 1:
                    print "WARNING: expected one entry string, found more..."
                entries.extend(log_entries)
            return entries
        else:
            return result

    def tag(self, tag_key=''):
        url = '%s/tag/%s' % (self.source, tag_key)
        #print url
        #GET:
        req = urllib2.urlopen(url)
        json_raw = req.read()
        #print "json from server: %s" % json_raw
        req.close()
        result = json.loads(json_raw)
        elist = []
        for e in result[tag_key]:
            m = Moment(data=e['data'], tags=e['tags'], created=e['created'], path=e['path'])
            #m = Moment(data=e['data'], tags=e['tags'], created=e['created'])
            elist.append(m)
        #return { tag_key:elist }
        return elist

    def dates(self):
        url = '%s/dates' % (self.source)
        req = urllib2.urlopen(url)
        json_raw = req.read()
        req.close()
        return json.loads(json_raw)

    def date(self, date_key=''):
        values = {}
        params = urllib.urlencode(values)
        if isinstance(date_key, Timestamp):
            ts = date_key
        else:
            ts = Timestamp(compact=date_key)
        url = '%s/date/%s' % (self.source, ts.compact())
        #print url
        #GET:
        req = urllib2.urlopen(url)
        json_raw = req.read()
        #print "json from server: %s" % json_raw
        req.close()
        result = json.loads(json_raw)
        elist = []
        for e in result[ts.compact()]:
            m = Moment(data=e['data'], tags=e['tags'], created=e['created'], path=e['path'])
            elist.append(m)
        return { ts.compact():elist }
        #return json.loads(json_raw)

    def entry(self, item=''):
        url = '%s/entry/%s' % (self.source, item)
        #GET:
        req = urllib2.urlopen(url)
        json_raw = req.read()
        req.close()
        #print json_raw
        e = json.loads(json_raw)
        #print e
        m = Moment(data=e['data'], tags=e['tags'], created=e['created'], path=e['path'])
        #print m
        return m

    def entries(self):
        url = '%s/entries' % (self.source)
        #GET:
        req = urllib2.urlopen(url)
        json_raw = req.read()
        req.close()
        result = json.loads(json_raw)
        elist = []
        for e in result['entries']:
            m = Moment(data=e['data'], tags=e['tags'], created=e['created'], path=e['path'])
            #m = Moment(data=e['data'], tags=e['tags'], created=e['created'])
            elist.append(m)
        return elist

    def search(self, look_for, data=False, limit=20):
        if data:
            url = '%s/search/data/%s' % (self.source, look_for)
        else:
            url = '%s/search/%s/%s' % (self.source, look_for, limit)
            #url = '%s/search/%s' % (self.source, look_for)
        #GET:
        req = urllib2.urlopen(url)
        json_raw = req.read()
        req.close()
        result = json.loads(json_raw)
        found = []
        if data:
            #for e in result['matches']:
            for e in result:
                m = Moment(data=e['data'], tags=e['tags'], created=e['created'], path=e['path'])
                #m = Moment(data=e['data'], tags=e['tags'], created=e['created'])
                found.append(m)
        else:
            #this should be a list of tags
            #found = result['matches']
            found = result
        return found

    def related(self, key):
        url = '%s/related/%s' % (self.source, key)
        #GET:
        req = urllib2.urlopen(url)
        json_raw = req.read()
        req.close()
        result = json.loads(json_raw)
        tags = result[key]
        return tags
        ## elist = []
        ## for e in result['entries']:
        ##     m = Moment(data=e['data'], tags=e['tags'], created=e['created'])
        ##     elist.append(m)
        ## return elist

    def sort(self, order='original'):
        url = '%s/sort/%s' % (self.source, order)
        req = urllib2.urlopen(url)
        return req.read()        
        
    def range(self, start=None, end=None):
        """
        """
        expect_entries = True
        if end:
            start = Timestamp(start)
            end = Timestamp(end)
            url = '%s/range/%s/%s' % (self.source, start.compact(), end.compact())
        elif start:
            start = Timestamp(start)
            url = '%s/range/%s' % (self.source, start.compact())
        else:
            url = '%s/range' % (self.source)
            expect_entries = False

        #print url
            
        req = urllib2.urlopen(url)
        response = req.read()
        req.close()
        if expect_entries:
            result = json.loads(response)
            elist = []
            for e in result['entries']:
                m = Moment(data=e['data'], tags=e['tags'], created=e['created'], path=e['path'])
                #m = Moment(data=e['data'], tags=e['tags'], created=e['created'])
                elist.append(m)
            return elist
        else:
            return response

    def clear(self):
        """
        call the load option on server
        """
        url = '%s/clear' % (self.source)
        req = urllib2.urlopen(url)
        return req.read()



if __name__ == "__main__":
    import doctest
    doctest.testmod()

