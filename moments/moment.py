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
An Moment is the foundation for a journal.
It does not require a timestamp, but most moments use one. 

In its most simple (text based) form, a moment consists of:
::

  * tags
  data
  \\n

With a timestamp:
::

  *timestamp tags
  data
  \\n

"""

from datetime import datetime
import string, re

from timestamp import Timestamp
from tag import Tags


class Moment(object):
    """
    Object to hold a unique Moment

    #*2011.07.03 09:16:58
    #by not having a separate moment and entry (no-timestamp)
    #we lose the ability to automatically assign a default timestamp
    #within the moment object itself
    #shouldn't be that big of a deal, since in practice we're often
    #creating moments withing the context of a journal
    #
    #if not, just pass in the timestamp on init

    also adding a parameter 'now' to set the timestamp automatically on init
    default is false
    """
    #def __init__(self, data=u'', tags=[], created=None, closed=None, placeholder=False, path=u''):
    def __init__(self, data=u'', tags=[], created='', path=u'', now=False):

        self.data = data        
        self.tags = Tags(tags)
        
        #could rename this to path potentially
        #self.source_file = None
        #*2011.06.21 09:59:10
        #now wishing it was just self.source
        #maybe both should be available?
        self.path = path
        self.source = path
        #*2011.08.14 18:56:17 
        #path implies a source and destination
        
        #self.created = ''
        
        #*2011.07.06 08:24:43
        #this may closely mimic the way Timestamp initializes
        #may want to leverage that
        #or just pass created and now values in to there
        
        if now:
            self.created = Timestamp()

        #elif type(created) == type(now):
        elif isinstance(created, datetime):
            self.created = Timestamp(created)

        #passed in an actual Timestamp here:
        elif isinstance(created, Timestamp):
            self.created = created

        elif isinstance(created, str) or isinstance(created, unicode):
            if created:
                self.created = Timestamp(created)
            else:
                self.created = created
                
        else:
            raise TypeError, "Unknown time format for moment created value: %s type: %s" % (created, type(created))
        
        #self.closed = closed
        
        #should not be stored in any database
        #self.placeholder = placeholder

    def as_dict(self):
        """
        return self as a dictionary suitable for JSON use
        """
        item = {}
        item['data'] = self.data
        item['created'] = str(self.created)
        item['tags'] = list(self.tags)
        item['path'] = str(self.path)

        #TODO
        #is item equivalent to a json.loads(json.dumps(self)) ???

        return item

    def is_equal(self, other, debug=False):
        """
        take another entry/moment
        see if our contents are equal
        """
        equal = True
        if not self.tags.is_equal(other.tags):
            equal = False
            if debug: print "Tags: %s (self) != %s (other)" % (str(self.tags), str(other.tags))
            
        #elif self.data != other.data:
        elif self.render_data() != other.render_data():
            equal = False
            if debug: print "Data: %s (self) != %s (other)" % (self.data, other.data)

        elif equal and str(self.created) != str(other.created):
            equal = False
            if debug: print "Created: %s (self) != %s (other)" % (str(self.created), str(other.created))

        return equal

    def render_first_line(self, comment=False):
        """
        render the date and the tags for the entry
        """
        if comment:
            line = '#' + str(self.created) + ' ' + ' '.join(self.tags) + "\n"
        else:
            line = '*' + str(self.created) + ' ' + ' '.join(self.tags) + "\n"
        return unicode(line)

    def has_data(self):
        return self.data.strip()

    def render_data(self):
        """
        return a textual representation of the entry data only
        """
        if self.data:
            #print "ENTRY DATA: %s" % type(self.data)
            #make sure that data is buffered with a blank line at the end
            #makes the resulting log easier to read.
            #if there are more than one blanklines, can leave them
            last_line = self.data.splitlines()[-1]
            #not re.match('\s', last_line) and
            
            #are there characters in the last line?  need to adjust if so:
            if re.search('\S', last_line):
                if re.search('\n$', last_line):
                    self.data += "\n"
                else:
                    #self.data += "\n"
                    #web entries added will end up with 3 newlines somehow
                    #but other entries created with a single string
                    #won't have enough new lines...
                    #should troubleshoot web entries
                    self.data += "\n\n"

            return unicode(self.data)
        else:
            #*2011.11.17 16:44:15
            #if loaded from a file, data almost always has newlines in it
            #shouldn't ever get here in that case
            
            #print "no data in this entry! : %s" % self.render_first_line()
            return unicode('')

    def render(self, include_path=False):
        """
        return a textual representation of the entry

        include_path assumed to be false in some places
        """
        entry = u''
        entry += self.render_first_line()

        #in most cases we do not want to show the source path,
        #(it can change easily and frequently, and is determined on read)
        #but when merging and reviewing (summarize)
        #it could be useful to see in a temporary file
        if include_path:
            entry += self.path + "\n"
            
        entry += self.render_data()
        return entry


