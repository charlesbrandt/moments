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
import StringIO, re, os
import codecs

from moment import Moment

import timestamp
from tag import Tags

class Log(StringIO.StringIO):
    """
    Log is an in memory buffer (StringIO) that holds
    a text format for a list of entries / moments. 

    The goal for this format is to be easy to create and update in a text editor

    For each entry:
    
       will create a Moment (with or without timestamp)
    """
    def __init__(self, filename=None):
        StringIO.StringIO.__init__(self)
        if filename:
            self.name = filename
        else:
            self.name = ''

        self.seek(0)

        # until we have entries (from to_entries or from_entries), assume we don't:
        self.has_entries = False

    def from_file(self, filename=None):
        """
        if the file exists, read in its contents

        otherwise set our filename and stay empty
        """
        if not self.name:
            #we don't have a file associated with the EntryList:
            if not filename:
                print "UNKNOWN FILE!"
                exit
            else:
                self.name = filename
                
        elif filename and filename != self.name:
            #ambiguous which file to use
            print "different file than what log was initialized with"
            exit
            
        else:
            #we have an original filename and none passed in
            #or the original filename equals the one passed in
            #should be good to go
            pass

        if os.path.exists(self.name):

            #f = open(self.name, "U")
            #2009.04.02 20:44:31 
            #very strange behavior when opening up utf-8 files
            #characters get reincoded
            #this is especially prominent when using check_feed.py
            #was using latin_1... going back to utf-8
            #f = codecs.open(self.name, encoding='latin_1')
            #codecs.ignore_errors(UnicodeDecodeError)            
            f = codecs.open(self.name, encoding='utf-8', errors='ignore')

            self.write(f.read())
            f.close

            self.seek(0)

        else:
            print "NO FILE ASSOCIATED WITH LOG: %s" % self.name

    def to_file(self, filename=None):
        """
        save our content to the file
        """
        name = None
        if filename is not None:
            name = filename
        elif self.name:
            name = self.name

        if name:
            #f = open(self.name, 'w')
            f = codecs.open(name, 'w', encoding='utf-8')
            self.seek(0)
            f.write(self.read())
            f.close()
        else:
            print "No log_name for this log"

    def from_entries(self, entries, omits=[], include_path=False):
        """
        take a collection of entries and put together a log buffer

        omit tags allow us to omit a certain tag on export/extract
        if omit tag is given,
        do not print the tag for any of the entries.
        """
        #need to make an explicit decision on where to start writing
        #with out that it is completely dependent on where the last
        #seek operation left the pointer in the file
        #could be the beginning, could be the end
        #need to be explicit about how from_entries operates though

        #think the right idea is that from_entries should over write any
        #other data in the log.  that means it should be extracted first
        #if it should be kept
        self.seek(0)
        
        for entry in entries:
            entry.tags.omit(omits)
            self.write(entry.render(include_path=include_path))

        if len(entries):
            self.has_entries = True

    def to_entries(self, add_tags=[], add_time=False, moments_only=False):
        """
        convert log to a list of entry objects (essentially what a log is)

        if moments_only is true, only Moments will be created
        
        if add_time is false, and moments_only is true,
        upon reaching an Entry only (*... ) (no timestamp)
        that information will be added to the previous Moment
        (this is useful when parsing data that was not originally intended to
        be used as part of a moment... it may contain lines that start with '*')
        """
        entries = []

        entry_regex = "\*"
        entry_search = re.compile(entry_regex)

        cur_entry = Moment()
        cur_entry.path = self.name

        new_entry = None
        
        try:
            self.seek(0)
            line = self.readline()
            line = unicode(line)
        except:
            print "Problem reading file"
            return entries

        #first line of a log should have an entry... this is our check
        if entry_search.match(line):
            self.has_entries = True
            while line:
                #we might have found a new entry...
                #see what kind, if any:
                (ts, line_tags) = timestamp.parse_line_for_time(line)
                if ts:
                    new_entry = Moment()
                    new_entry.created = timestamp.Timestamp(ts)
                elif entry_search.match(line):            
                    if not moments_only:
                        new_entry = Moment()
                    elif add_time and moments_only:
                        #ok to make a default time for the entry
                        new_entry = Moment()
                        print "no timestamp found in this entry"
                    else:
                        #must be moments only,
                        #but we don't want to add a timestamp
                        #just include the data with the previous moment
                        new_entry = None

                if new_entry:
                    #finish up last entry...
                    #only need to add if it had information
                    if cur_entry.data or cur_entry.tags:
                        entries.append(cur_entry)

                    new_entry.path = self.name

                    current_tags = line_tags.strip().split()

                    if add_tags:
                        temp_tags = add_tags[:]
                        for t in current_tags:
                            if t not in temp_tags:
                                temp_tags.append(t)
                        current_tags = temp_tags

                    new_entry.tags.extend(current_tags)
                    cur_entry = new_entry
                    new_entry = None

                else:
                    # only want to add the entry itself
                    cur_entry.data += line

                line = unicode(self.readline())
                
            #need to get the last entry from the file, if there is one.
            if cur_entry.data:
                entries.append(cur_entry)

        #if not, don't scan
        else:
            print "File does not start with an entry: %s" % self.name
            
        return entries


