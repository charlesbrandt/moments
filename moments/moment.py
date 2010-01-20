"""
A Moment object is a subclass of Entry

Adds a timestamp and corresponding helper functions to an Entry
"""

from datetime import datetime
import string, re

#from webhelpers.html import url_escape
#or use urllib.quote(path)
#import urllib

from timestamp import Timestamp
from tags import Tags

from entry import Entry

class Moment(Entry):
    """
    Object to hold a unique Moment (Journal Entry with Time)
    """
    def __init__(self, data=u'', tags=[], created=None, closed=None, placeholder=False, path=u''):

        Entry.__init__(self, data, tags, path)
        
        now = datetime.now()
        if not created:
            self.created = Timestamp()
        elif type(created) == type(now):
            self.created = Timestamp(created)

        #*2009.08.08 17:58:40 not sure why this 'else' was commented
        #if causing incorrect behavior should document that.
        else:
            #assuming we passed in an actual Timestamp here:
            self.created = created
        
        self.closed = closed
        
        #should not be stored in any database
        self.placeholder = placeholder

    def total_time(self):
        #could also check sub_entries to see how much time was accounted for
        #see if it gets close
        return self.closed.datetime - self.created.datetime

    def is_placeholder(self):
        return self.placeholder

    def to_placeholder(self, destination_log):
        if not self.placeholder:
            data = u" [moved / exported to: %s]\n\n" % destination_log
            new = Entry(data, self.created, self.closed, [destination_log], True)
            return new
        else:
            return self

    def render_date(self, date=None):
        if not date:
            date = self.created
        return str(date)

    def render_compact(self):
        return self.created.compact()

    def render_first_line(self, format='text', link_tags=True):
        """
        render the date and the tags for the entry
        """
        text_time = str(self.created)

        line = ''
        if format == 'text':
            line = '*' + text_time + ' ' + ' '.join(self.tags) + "\n"
        elif format == 'html':
            tags = ''
            if link_tags:
                for t in self.tags:
                    tags += u'<a href="/tags/%s.html">%s</a> ' % (t, t)
            else:
                tags = ' '.join(self.tags)
            line = u'<div class="entry_header"><span class="asterisk">*</span><span class="date">%s </span><span class="tags">%s</span></div>' % (text_time, tags)
        else:
            print "Unknown format: %s" % format
        return unicode(line)

    def render_comment(self):
        """
        render the date and the tags for the entry as a comment
        """
        text_time = str(self.created)
        
        line = '#'
        line += text_time + " " + ' '.join(self.tags)
        line += "\n"
        return unicode(line)

