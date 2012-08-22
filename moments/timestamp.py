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
*2010.10.24 11:49:23
much of this functionality exists in the dateutil included with python
http://labix.org/python-dateutil
I didn't know about that module at the time
Its parse function is really nice.

*2010.03.16 10:56:36 todo
would be nice if format was more generalized
it is difficult when there are different versions of a string
depending on the degree of accuracy. (seconds, no seconds, etc)

*2009.07.17 07:36:52
considering that timestamps have different formats
might be nice to associate that format with the object instance
and make it settable/configurable.

depending on format
could have different output for date, time, accuracies, etc.

*2010.03.16 10:20:38
some time ago...
moved time to be the first keyword argument
that way Timestamp objects can be initialized from a standard python
datetime object, without specifying the time keyword

*2009.03.14 18:23:13 subclass datetime why_not
would be nice if this were a subclass of datetime
with special formatters built in
tried this last week with ill effects, because...

datetime objects in python are immutable
class attributes like year, month, and day are read-only

subclassing requires overriding __new__, not __init___
http://stackoverflow.com/questions/399022/why-cant-i-subclass-datetime-date
http://www.python.org/doc/current/reference/datamodel.html#object.__new__

due to multiple ways of initializing, we don't want to require that
year, month, day
be passed in, like datetime does

could add those arguments to the init function if that was needed
by those using Timestamp objects in place of datetime objects

"""

from datetime import datetime, timedelta, date
from datetime import time as dttime
from time import strptime
import time as pytime

import re

time_format = "%Y.%m.%d %H:%M"

def has_timestamp(line):
    (ts, remainder) = parse_line_for_time(line)
    if ts:
        return True
    else:
        return False

def get_timestamp(line):
    #original way:
    #removes the leading "*"
    #return line[1:17]
    
    ts, tags = parse_line_for_time(line)
    return ts

def parse_line_for_time(line):
    """
    look at the line, determine if there is a timestamp
    return the timestamp, and the remainder if so
    """
    #most specific
    second_regex = "[-\*](19|20)\d\d[- /.](0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01]) \d\d:\d\d:\d\d"
    second_search = re.compile(second_regex)

    minute_regex = "[-\*](19|20)\d\d[- /.](0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01]) \d\d:\d\d"
    #time_search = "\*\d\d\d\d.\d\d.\d\d \d\d:\d\d"
    minute_search = re.compile(minute_regex)

    #hopefully optionally match a leading '-' or '*'
    #day_regex = "[-\*]*(19|20)\d\d[- /.](0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])"
    #*2009.03.03 14:38:58
    #requiring the leading '*' now...
    #old logs should be converted manually if not updated at this point
    day_regex = "[-\*](19|20)\d\d[- /.](0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])"
    day_search = re.compile(day_regex)

    s = second_search.match(line)
    m = minute_search.match(line)
    d = day_search.match(line)
    #print s.span()
    if s:
        ts = line[s.span()[0]:s.span()[1]] #s.expand()
    elif m:
        ts = line[m.span()[0]:m.span()[1]] #s.expand()
        #ts = m.expand()
    elif d:
        ts = line[d.span()[0]:d.span()[1]] #s.expand()
        #ts = d.expand()
    else:
        ts = None

    if ts:
        remainder = line[len(ts):]
    else:
        entry_regex = "\*"
        entry_search = re.compile(entry_regex)
        if entry_search.match(line):
            remainder = line.split('*')[1]
        else:
            remainder = ''

    return [ts, remainder]

class Timestamp(object):
    """
    Timestamps have different ways of being formatted, and 
    this object is a common place to store these. 

    compact and cstamp are the same thing.
    """

    def __init__(self, auto=None, tstamp=None, cstamp=None, compact=None,
                 now=True, format=None, accuracy=None):
        #this is the internal datetime object:
        #it is available externally via self.datetime
        self.dt = None
        
        #might be handy to know what we determined
        #after parsing line
        #or remembering if it gets set elsewhere
        #
        #NOTE: if it gets passed in, it will get overwritten if
        #string conversion accurracy is different.
        self.accuracy = accuracy
        self.format = format

        if auto is not None:
            if isinstance(auto, datetime):
                self.dt = auto
            elif isinstance(auto, Timestamp):
                #this doesn't seem to work:
                #self = auto
                self.dt = auto.dt
            elif isinstance(auto, str) or isinstance(auto, unicode):
                #self.from_text(auto)
                self.parse(auto)
            else:
                #print "Unknown auto item: %s (type: %s)" % (auto, type(auto))
                raise ValueError, "Unknown Timestamp start value: %s of type %s" % (auto, type(auto))

        elif tstamp:
            self.from_text(tstamp)
        elif cstamp:
            self.from_compact(cstamp)
        elif compact:
            self.from_compact(compact)
        elif now:
            self.dt = datetime.now()

        
    def __getattr__(self, name):
        """
        if the Timestamp class doesn't have the attribute,
        check if the associated datetime object does have the attribute.
        """
        if name == 'datetime' or name == 'time':
            return self.__getattribute__('dt')
        elif name in dir(self.dt):
            return self.dt.__getattribute__(name)
        else:
            raise AttributeError

    def __setattr__(self, name, value):
        if name == 'datetime' or name == 'dt':
            object.__setattr__(self, 'dt', value)
        #get all of the typical assignments:
        else:
            object.__setattr__(self, name, value)

    def __str__(self):
        text_time = ''
        if self.dt.strftime("%S") != "00":
            text_time = self.dt.strftime("%Y.%m.%d %H:%M:%S")
        elif self.dt.strftime("%H:%M") != "00:00":
            text_time = self.dt.strftime("%Y.%m.%d %H:%M")
        else:
            text_time = self.dt.strftime("%Y.%m.%d")
        return text_time

    #aka auto_text
    def parse(self, text_time):
        """
        Attempt to automatically determine the time format in use

        similar to dateutil.parser parse

        but no timezones

        note:
        TypeError: can't compare offset-naive and offset-aware datetimes
        from dateutil.parser import parse
        self.dt = parse(text_time)

        """
        if re.search('T', text_time) and re.search(':', text_time):
            if re.search('Z', text_time):
                self.from_gps(text_time)
            else:
                self.from_google_calendar(text_time)
                
        elif re.search('T', text_time):
            self.from_apple_compact(text_time)

        elif re.search("-", text_time) or re.search("/", text_time) or re.search("\.", text_time):
            self.from_text(text_time)
        else:
            self.from_compact(text_time)

    def round(self, accuracy=None):
        """
        return a new timestamp object with the desired accuracy
        """
        c = self.compact(accuracy)
        return Timestamp(compact=c)

    def text(self, accuracy=None):
        """
        return a string representation of our internal datetime object
        with a format like:
        YYYYMMDDHHMMSS
        controlled by 'accuracy'
        """
        #if it was not passed in, see if it has been set elsewhere
        if not accuracy and self.accuracy:
            accuracy = self.accuracy

        if accuracy == 'year':
            return self.dt.strftime("%Y")
        elif accuracy == 'month':
            return self.dt.strftime("%Y.%m")
        elif (accuracy == 'day') or ((self.dt.hour == 0) and (self.dt.minute == 0) and (self.dt.second == 0)):
            return self.dt.strftime("%Y.%m.%d")
        elif accuracy == 'hour':
            return self.dt.strftime("%Y.%m.%d %H")
        elif (accuracy == 'minute') or (self.dt.second == 0):
            return self.dt.strftime("%Y.%m.%d %H:%M")
        else:
            return self.dt.strftime("%Y.%m.%d %H:%M:%S")

    #was time_to_tstamp
    def compact(self, accuracy=None):
        """
        return a string representation of our internal datetime object
        with a format like:
        YYYYMMDDHHMMSS
        controlled by 'accuracy'
        """
        #if it was not passed in, see if it has been set elsewhere
        if not accuracy and self.accuracy:
            accuracy = self.accuracy

        if accuracy == 'year':
            return self.dt.strftime("%Y")
        elif accuracy == 'month':
            return self.dt.strftime("%Y%m")
        elif (accuracy == 'day') or ((self.dt.hour == 0) and (self.dt.minute == 0) and (self.dt.second == 0)):
            return self.dt.strftime("%Y%m%d")
        elif accuracy == 'hour':
            return self.dt.strftime("%Y%m%d%H")
        elif (accuracy == 'minute') or (self.dt.second == 0):
            return self.dt.strftime("%Y%m%d%H%M")
        else:
            return self.dt.strftime("%Y%m%d%H%M%S")

    def filename(self, suffix=".txt"):
        """
        often need to generate a filename from a timestamp
        this makes it easy!
        """
        return self.compact(accuracy='day') + suffix

    def epoch(self):
        """
        convert Timestamps to a 'seconds since epoc' format
        
        return the current timestamp object as the number of seconds since the
        epoch.  aka POSIX timestamp
        aka utime (?)
        *2009.11.04 13:57:55
        http://stackoverflow.com/questions/255035/converting-datetime-to-posix-time
        """
        #import time, datetime

        return pytime.mktime(self.dt.timetuple())

    def from_epoch(self, posix_time):
        """
        accept a posix time and convert it to a local datetime
        (in current Timestamp)
        http://docs.python.org/library/datetime.html#datetime.datetime.fromtimestamp
        see also datetime.utcfromtimestamp()
        """
        self.dt = datetime.fromtimestamp(posix_time)

    #was tstamp_to_time
    def from_compact(self, text_time):
        """
        take a string of the format:
        YYYYMMDDHHMMSS
        return a python datetime object
        """
        if len(text_time) == 14:
            self.dt = datetime(*(strptime(text_time, "%Y%m%d%H%M%S")[0:6]))
            self.accuracy = 'second'
        elif len(text_time) == 12:
            self.dt = datetime(*(strptime(text_time, "%Y%m%d%H%M")[0:6]))
            self.accuracy = 'minute'
        elif len(text_time) == 10:
            self.dt = datetime(*(strptime(text_time, "%Y%m%d%H")[0:6]))
            self.accuracy = 'hour'
        elif len(text_time) == 8:
            self.dt = datetime(*(strptime(text_time, "%Y%m%d")[0:6]))
            self.accuracy = 'day'
        elif len(text_time) == 6:
            self.dt = datetime(*(strptime(text_time, "%Y%m")[0:6]))
            self.accuracy = 'month'
        elif len(text_time) == 4:
            self.dt = datetime(*(strptime(text_time, "%Y")[0:6]))
            self.accuracy = 'year'
        else:
            #some other format
            #self.dt = None
            raise AttributeError, "Unknown compact time format: %s" % text_time
        return self.dt

    #was log.text_to_time
    #in ruby: parse
    def from_text(self, text_time):
        """
        take a string of the format:
        YYYY.MM.DD HH:MM
        return a python datetime object
        """
        #removed leading char if needed
        if re.match("[-\*]", text_time):
            text_time = text_time[1:]

        if re.search("-", text_time):
            format = "%Y-%m-%d %H:%M:%S"
        elif re.search("/", text_time):
            format = "%Y/%m/%d %H:%M:%S"
        else:
            format = "%Y.%m.%d %H:%M:%S"

        if len(text_time) > 19:
            #2007-05-03T15:56:05-04:00
            #
            #but what about 2009-07-17 07:14:17.003537?
            #truncating for now
            #TODO: accept micro seconds
            text_time = text_time[:19]
            time = datetime(*(strptime(text_time, "%Y-%m-%dT%H:%M:%S")[0:6]))
            self.accuracy = 'second'
            
        elif len(text_time) == 19:
            # this only works with python 2.5
            # (current default is 2.4.4 for zope)
            #return datetime.strptime(text_time, self.text_time_format)
            # e.g. "%Y.%m.%d %H:%M:%S"
            time = datetime(*(strptime(text_time, format)[0:6]))
            self.accuracy = 'second'
        elif len(text_time) == 16:
            # e.g. "%Y.%m.%d %H:%M"
            time = datetime(*(strptime(text_time, format[:14])[0:6]))
            self.accuracy = 'minute'
            
        elif len(text_time) == 10:
            # e.g. "%Y.%m.%d"
            time = datetime(*(strptime(text_time, format[:8])[0:6]))
            self.accuracy = 'day'
        else:
            #some other format
            #time = None
            raise ValueError, "Unknown time string format passed to Timestamp.from_text: %s (type: %s)" % (text_time, type(text_time))

        self.dt = time
        return time

    def from_text2(self, text_time):
        """
        Month DD, YYYY
        """
        months = [ "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December" ]
        #get rid of double spacing, if it exists
        text_time = text_time.replace("  ", " ")
        (month_s, day_s, year_s) = text_time.split(' ')
        if month_s in months:
            month = months.index(month_s) + 1
            #print month
        else:
            print "Couldn't find: %s" % month_s
            month = None
        #get rid of ',' after date
        if re.search(',', day_s):
            day = int(day_s[:-1])
        else:
            day = int(day_s)
            
        year = int(year_s)
        #print "Day: %s, Year: %s" % (day, year)
        compact = "%s%02d%02d" % (year, month, day)
        #try:
        self.dt = datetime(*(strptime(compact, "%Y%m%d")[0:6]))
        self.accuracy = 'day'
        #stamp = Timestamp(compact=compact)
        #except:
        #    print "error making Timestamp from: %s" % compact
        

    def from_gps(self, text_time, offset=-4):
        """
        take a string of the gps format:
        apply a delta for local time zone
        return a python datetime object
        """
        if len(text_time) == 20:
            self.dt = datetime(*(strptime(text_time, "%Y-%m-%dT%H:%M:%SZ")[0:6]))
            self.accuracy = 'second'
        else:
            #some other format
            self.dt = None
            print "Unknown gps date format: %s" % text_time
            exit()

        off = timedelta(hours=offset)
        self.dt += off
        return self.dt

    #was tstamp_to_time
    def from_apple_compact(self, text_time):
        """
        take a string of the format:
        YYYYMMDDTHHMMSS  (where T is the character 'T')
        return a python datetime object
        """
        #get rid of trailing Z
        if len(text_time) == 16:
            text_time = text_time[:15]
            
        if len(text_time) == 15:
            self.dt = datetime(*(strptime(text_time, "%Y%m%dT%H%M%S")[0:6]))
            self.accuracy = 'second'
        elif len(text_time) == 13:
            self.dt = datetime(*(strptime(text_time, "%Y%m%dT%H%M")[0:6]))
            self.accuracy = 'minute'
        elif len(text_time) == 11:
            self.dt = datetime(*(strptime(text_time, "%Y%m%dT%H")[0:6]))
            self.accuracy = 'hour'
        elif len(text_time) == 8:
            self.dt = datetime(*(strptime(text_time, "%Y%m%d")[0:6]))
            self.accuracy = 'day'
        elif len(text_time) == 6:
            self.dt = datetime(*(strptime(text_time, "%Y%m")[0:6]))
            self.accuracy = 'month'
        elif len(text_time) == 4:
            self.dt = datetime(*(strptime(text_time, "%Y")[0:6]))
            self.accuracy = 'year'
        else:
            #some other format
            self.dt = None
        return self.dt

    def apple_compact(self, accuracy=None):
        """
        take a python datetime object
        return a string representation of that time
        YYYYMMDDTHHMMSS
        """
        return self.dt.strftime("%Y%m%dT%H%M%S")

    def from_google_calendar(self, text_time):
        """
        take a string of the format:
        YYYY-MM-DDTHH:MM:SS.000-04:00  (where T is the character 'T')
        return a python datetime object

        Note that timezone feature is not yet working
        """
        ## if len(text_time) == 29:
        ##     #TODO: incorporate time zone when available
        ##     #self.dt = datetime(*(strptime(text_time, "%Y-%m-%dT%H:%M:%S.000-0.:00")[0:6]))

        ##     #note:
        ##     #TypeError: can't compare offset-naive and offset-aware datetimes
        ##     from dateutil.parser import parse
        ##     self.dt = parse(text_time)
        ## elif len(text_time) == 19:
        if len(text_time) == 29:
            #discarding timezone in this case:
            text_time = text_time[:19]
        if len(text_time) == 19:
            self.dt = datetime(*(strptime(text_time, "%Y-%m-%dT%H:%M:%S")[0:6]))
            self.accuracy = 'second'
        elif len(text_time) == 16:
            self.dt = datetime(*(strptime(text_time, "%Y-%m-%dT%H:%M")[0:6]))
            self.accuracy = 'minute'
        elif len(text_time) == 13:
            self.dt = datetime(*(strptime(text_time, "%Y-%m-%dT%H")[0:6]))
            self.accuracy = 'hour'
        elif len(text_time) == 10:
            self.dt = datetime(*(strptime(text_time, "%Y-%m-%d")[0:6]))
            self.accuracy = 'day'
        elif len(text_time) == 7:
            self.dt = datetime(*(strptime(text_time, "%Y-%m")[0:6]))
            self.accuracy = 'month'
        elif len(text_time) == 4:
            self.dt = datetime(*(strptime(text_time, "%Y")[0:6]))
            self.accuracy = 'year'
        else:
            #some other format
            self.dt = None
        return self.dt

    def google_calendar(self, accuracy=None):
        """
        take a python datetime object
        return a string representation of that time
        YYYYMMDDTHHMMSS
        """
        return self.dt.strftime("%Y-%m-%dT%H:%M:%S")

    ## def from_blog(self, text):
    ##     """
    ##     the following format is often used in blogs
    ##     """
    ##     pass

    ## def from_format(self, text, format):
    ##     """
    ##     use the supplied format to parse the text
    ##     """
    ##     pass

    
    def now(self):
        """
        update the timestamp to be the current time (when now() is called)
        """
        self.dt = datetime.now()

    def future(self, years=0, weeks=0, days=0,
               hours=0, minutes=0, seconds=0):
        """
        return a new Timestamp object that is in the future
        according to parameters

        months are not included since it is tricky to convert those into days
        (months are not consistent in length)
        and days are what we need to boil the distance down to.
        
        could revisit that in the future (hehe)
        the tricky cases will be when the function is called
        on the 31st of a month,
        and told to go into the future to a month that does not have 31 days.
        Should it roll back to the 30th of that future month? (or 28th in Feb?)
        or should it go forward?
        """
        future = self.dt
        if years:
            year = timedelta(365)
            future = future + (years * year)

        if weeks:
            week = timedelta(7)
            future = future + (weeks * week)

        if days:
            future = future + timedelta(days)

        if hours:
            future = future + timedelta(hours=hours)

        if minutes:
            future = future + timedelta(minutes=minutes)

        if seconds:
            future = future + timedelta(seconds=seconds)

        return Timestamp(future)

    def past(self, years=0, weeks=0, days=0,
               hours=0, minutes=0, seconds=0):
        """
        return a new Timestamp object that is in the past
        according to parameters
        """
        past = self.dt
        if years:
            year = timedelta(365)
            past = past - (years * year)

        if weeks:
            week = timedelta(7)
            past = past - (weeks * week)

        if days:
            past = past - timedelta(days)

        if hours:
            past = past - timedelta(hours=hours)

        if minutes:
            past = past - timedelta(minutes=minutes)

        if seconds:
            past = past - timedelta(seconds=seconds)

        return Timestamp(past)

    def future_month(self, months=1):
        """
        because future and past does not handle months,
        handle this separately
        """
        next_month = self.month + months
        if next_month >= 13:
            years = next_month / 12
            next_month = next_month % 12
            #next_month = 1
            year = self.year + years
        else:
            year = self.year
            
        next_compact = "%s%02d" % (year, next_month)
        next_month_stamp = Timestamp(compact=next_compact)
        return next_month_stamp

    def past_month(self, months=1):
        prior_month = self.month - months
        if prior_month <= 0:
            years = 1 + (abs(prior_month) / 12)
            year = self.year - years
            prior_month = 12 - (abs(prior_month) % 12)
        else:
            year = self.year

        prior_compact = "%s%02d" % (year, prior_month)
        prior_month_stamp = Timestamp(compact=prior_compact)
        return prior_month_stamp

    def is_in(self, timerange):
        """
        check if we are contained in the given timerange

        this should be equivalent to:
        timerange.has(timestamp)
        """
        #print "Datetime: %s" % self.datetime
        #print "Start Datetime: %s" % timerange.start.datetime
        #print "End Datetime: %s" % timerange.end.datetime

        #print type(self.datetime)
        #print type(self.dt)
        #print type(timerange.start.datetime)

        if ( (self.datetime > timerange.start.datetime) and
             (self.datetime < timerange.end.datetime) ):
            return True
        else:
            return False
        

    # the following are picked up by __getattr__()
    # which pulls them from the self.dt (datetime)

    ## def year(self):
    ##     """
    ##     return a string for our year (YYYY)
    ##     """
    ##     return self.dt.strftime("%Y")
        
    ## def month(self):
    ##     """
    ##     return a string for our month (MM)
    ##     """
    ##     return self.dt.strftime("%m")

    ## def day(self):
    ##     """
    ##     return a string for our day (DD)
    ##     """
    ##     return self.dt.strftime("%d")

    ## def hour(self):
    ##     """
    ##     return a string for our hour (HH) (24 hour)
    ##     """
    ##     return self.dt.strftime("%H")

    ## def minute(self):
    ##     """
    ##     return a string for our minute (MM)
    ##     """
    ##     return self.dt.strftime("%M")

    ## def second(self):
    ##     """
    ##     return a string for our second (SS)
    ##     """
    ##     return self.dt.strftime("%S")

class Timerange(object):
    """
    Timerange holds a start and end python datetime

    trange can either be a string representing two timestamps separated
    by a '-'
    or just a simple tstamp string
    in which case it will be evaluated as a range based on accuracy

    *2011.07.06 19:21:53
    start can be either a text based string range "start-end"
    or a timestamp object representing the start of the range

    *2011.07.06 22:15:06
    merging in RelativeRange functions

    Relative range was a 
    class to quickly get ranges relative to 'now' (or start)
    sometimes these are more complex than just 'future' and 'past' on Timestamp

    results in timeranges from specific functions
    """

    def __init__(self, start, end=None, name='', end_is_now=False):
        """
        remember that start can be a string based range value:
        'YYYYMMDD-YYYYMMDD'
        """
        #this may get set in a number of different places
        self.end = None
        if isinstance(start, str) or isinstance(start, unicode):
            self.from_text(start)
        else:
            #this should handle all different cases
            self.start = Timestamp(start)

        if end:
            #this should handle
            #all of the different conditions / formats / types
            #that end could be in
            self.end = Timestamp(end)
        elif end_is_now:
            #end = datetime.now()
            self.end = Timestamp()
        elif not self.end:
            #default should set self.end now
            self.default()
            #temp = self.default()
            #self.end = temp.end
        else:
            #end was not passed in,
            #but self.end must have been set elsewhere (from_text())
            #all should be ok then
            pass


        #print type(self)
        #print "Name: ->%s<-" % name
        #name could be a string indicating the type of relation
        #e.g.
        #last month, this month, next_month
        self._name = name

    #name is a property on the cycle.Month
    #can't set a property in parent class in that case
    def _get_name(self):
        return self._name
    
    name = property(_get_name)
        
    def __str__(self):
        if self.start == self.end:
            return self.start.compact()
        else:
            return '-'.join( [self.start.compact(), self.end.compact()] )

    def as_tuple(self):
        return (self.start, self.end)

    def has(self, timestamp):
        """
        return true if timestamp is in our range

        see also Timestamp.is_in(Timerange)
        """
        pass

    def from_text(self, trange):
        """
        will work with either a simple timestamp string
        or a string with a - separating two timestamp strings
        
        check the tstamp for a range of times
        split if found
        return the range start and end
        """
        start = ''
        end = ''

        #check for a '-' indicating a YYYYMMDD-YYYYMMDD string
        if re.search('-', trange):
            (start, end) = trange.split('-')
        else:
            start = trange

        #(start, default_end) = self.from_tstamp(start)
        self.start = Timestamp(compact=start)

        #if we found an explicit end in the string, use it
        if end:
            #end = Timestamp().from_compact(end)
            self.end = Timestamp(compact=end)
            #end = ts.time
            #end = tstamp_to_time(end)
        else:
            self.default()
            #end = self.end

        #self.start = start
        #self.end = end
        return (self.start, self.end)


    def biggest_cycle(self):
        """
        determine what the biggest cycle is in our range...
        i.e. year, month, day
        """
        #can't do anything if there is no end in the range
        if not self.end:
            return None
        else:
            diff = self.end.datetime - self.start.datetime
            if diff.days >= 365:
                print "YEAR"
                return "year"
            elif diff.days >= 31:
                print "MONTH"
                return "month"
            elif diff.days >= 28:
                print "MONTH (maybe)"
                diff_m = self.end.month - self.start.month
                #should check here if the month and days increment accordingly
                if (diff_m == 1) and (self.end.day >= self.start.day):
                    return "month"
                elif (diff_m > 1):
                    return "month"
            elif diff.days >= 7:
                print "WEEK"
                return "week"
            elif diff.days >= 1:
                print "DAY"
                return "day"
            else:
                return "hour"

    def months(self, overlap_edges=True):
        """
        return a list of all months contained in self
        (this could also be an iterator)

        if overlap_edges is set, may extend beyond the current range
        rounding to the nearest full month on each end
        """
        #rr = RelativeRange()
        current = self.start.round("month")
        end = self.end.round("month")
        months = []
        while str(current) != str(end):
            #month = rr.month(current)
            month = self.month(current)
            months.append(month)
            current = current.future_month(months=1)
        return months
                    
    def days(self, overlap_edges=True):
        """
        return a list of all days contained in self
        (this could also be an iterator)

        if overlap_edges is set, may extend beyond the current range
        rounding to the nearest full day on each end
        """
        #rr = RelativeRange()
        current = self.start.round("day")
        end = self.end.round("day")
        days = []
        while str(current) != str(end):
            #day = rr.day(current)
            day = self.day(current)
            days.append(day)
            current = current.future(days=1)
        return days

    #Relative Range functions
    #the following functions could be used independent of a Timerange context
    #but keeping them here for easier access
    def default(self):
        """
        checks the accuracy of the start timestamp
        calls correct method automatically to generate a range
        based on that accuracy
        """
        accuracy = self.start.accuracy
        if accuracy and accuracy != "second":
            if accuracy == "year":
                return self.year()
            elif accuracy == "month":
                return self.month()
            elif accuracy == "day":
                return self.day()
            elif accuracy == "hour":
                return self.hour()
            elif accuracy == "minute":
                return self.minute()
        else:
            #print "Invalid accuracy for automatic Timerange: %s" % self.start.accuracy
            #if we can't make an intelligent choice about the range
            #based on the accuracy of the start
            #then we can just default to now
            self.end = Timestamp()
            return self

    def year(self, timestamp=None):
        """
        return a range for the year that timestamp falls in
        """
        if timestamp:
            #want to make sure we normalize to an acutal Timestamp object
            timestamp = Timestamp(timestamp)
        else:
            timestamp = self.start
        start_compact = "%s" % (timestamp.year)
        end_compact = "%s1231235959" % (timestamp.year)
        self.end = Timestamp(compact=end_compact)
        return Timerange("%s-%s" % (start_compact, end_compact))

    def month(self, timestamp=None):
        """
        return a range for the month that timestamp falls in
        """
        if timestamp:
            #want to make sure we normalize to an acutal Timestamp object
            timestamp = Timestamp(timestamp)
        else:
            timestamp = self.start

        #start_compact = "%s%02d" % (timestamp.year, timestamp.month)
        #month_start_stamp = Timestamp(compact=start_compact)

        month_start_stamp = timestamp.round(accuracy="month")
        
        next_month_stamp = timestamp.future_month()
        #print "Next month: %s" % next_month
        #print "Next month stamp: %s" % next_month_stamp
        sec = timedelta(seconds=1)
        month_end = next_month_stamp.datetime - sec
        #print month_end
        month_end_stamp = Timestamp(month_end)
        self.end = month_end_stamp
        return Timerange(start=month_start_stamp, end=month_end_stamp)

    def week(self, timestamp=None, week_start=0):
        """
        uses date.weekday() to determine position in the week
        Monday is 0, (default week_start)
        if another day should be used, specify in week_start
        """
        if timestamp:
            #want to make sure we normalize to an acutal Timestamp object
            timestamp = Timestamp(timestamp)
        else:
            timestamp = self.start

        #round timestamp to the beginning of the day:
        day = timestamp.round(accuracy='day')
        timestamp = day

        date = timestamp.datetime.date()
        weekday = date.weekday()
        if weekday >= week_start:
            go_back = weekday - week_start
            go_forward = 6 - weekday
        else:
            go_back = weekday - week_start + 6 + 1
            go_forward = week_start - weekday - 1

        go_forward += 1
        #print "back: %s, forward: %s" % (go_back, go_forward)
        week_start_stamp = timestamp.past(days=go_back)
        week_end_plus = timestamp.future(days=go_forward)
        sec = timedelta(seconds=1)
        week_end = week_end_plus.datetime - sec
        #print month_end
        week_end_stamp = Timestamp(week_end)
        self.end = week_end_stamp
        return Timerange(start=week_start_stamp, end=week_end_stamp)
        

    def day(self, timestamp=None):
        """
        return a range for the day that timestamp falls in
        """
        if timestamp:
            #want to make sure we normalize to an acutal Timestamp object
            timestamp = Timestamp(timestamp)
        else:
            timestamp = self.start

        today_start_stamp = timestamp.round(accuracy="day")
        
        tomorrow_stamp = timestamp.future(days=1)
        sec = timedelta(seconds=1)
        today_end = tomorrow_stamp.datetime - sec
        today_end_stamp = Timestamp(today_end)
        self.end = today_end_stamp
        return Timerange(start=today_start_stamp, end=today_end_stamp)

    def hour(self, timestamp=None):
        """
        return a range for the day that timestamp falls in
        """
        if timestamp:
            #want to make sure we normalize to an acutal Timestamp object
            timestamp = Timestamp(timestamp)
        else:
            timestamp = self.start

        start_stamp = timestamp.round(accuracy="hour")
        
        next_stamp = timestamp.future(hours=1)
        sec = timedelta(seconds=1)
        hour_end = next_stamp.datetime - sec
        end_stamp = Timestamp(hour_end)
        self.end = end_stamp        
        return Timerange(start=start_stamp, end=end_stamp)

    def minute(self, timestamp=None):
        """
        return a range for the minute that timestamp falls in
        """
        if timestamp:
            #want to make sure we normalize to an acutal Timestamp object
            timestamp = Timestamp(timestamp)
        else:
            timestamp = self.start

        start_stamp = timestamp.round(accuracy="minute")
        
        next_stamp = timestamp.future(minutes=1)
        sec = timedelta(seconds=1)
        minute_end = next_stamp.datetime - sec
        end_stamp = Timestamp(minute_end)
        self.end = end_stamp
        return Timerange(start=start_stamp, end=end_stamp)

    def year_past(self, timestamp=None):
        """the last 12 months"""
        if timestamp:
            #want to make sure we normalize to an acutal Timestamp object
            timestamp = Timestamp(timestamp)
        else:
            timestamp = self.start

        end_compact = timestamp.compact()
        last_year = timestamp.past(years=1)
        start_compact = last_year.compact()
        return Timerange("%s-%s" % (start_compact, end_compact))

    def this_month(self):
        return self.month(self.start)

    def last_month(self):
        #last_compact = "%s%02d" % (self.start.
        last_month_ts = self.start.past_month()
        return self.month(last_month_ts)

    def next_month(self):
        #last_compact = "%s%02d" % (self.start.
        next_month_ts = self.start.future_month()
        return self.month(next_month_ts)
        
    #should see future and past operations on Timestamp now
    #def this_week_last_year(today=date.today()):
    def this_week_last_year(today=None):
        if not today:
            today = datetime.combine(date.today(), dttime(0))
        #today = datetime.datetime.now()

        #could use date to same effect,
        #but that would require exceptions/checks in timestamp for type
        #today.hour = 0
        #today.minute = 0
        #today.second = 0
        #these are read-only attributes

        year = timedelta(365)
        last_year = today - year
        start = last_year - timedelta(4)
        end = last_year + timedelta(4)
        #stamp = start.strftime("%Y%m%d") + '-' + end.strftime("%Y%m%d")

        return Timerange(start=start, end=end)
        #stamp = str(tr)
        #return stamp


class Year(object):
    def __init__(self):
        self.months = []

class Month(Timerange):
    """
    using this to hold a collection of days (or weeks?)
    to ultimately render those days, and their content (summary)
    to some other representation (HTML, areaui, etc)
    """
    def __init__(self, tstamp=None, **kwargs):
        Timerange.__init__(self, tstamp, **kwargs)

        #test to make sure we were sent an actual month,
        #rr = RelativeRange(self.start)
        #rr = Timerange(self.start, name="relative")
        #rr_month = rr.month()
        rr_month = self.month()
        if rr_month.start.datetime != self.start.datetime:
            print "Moving start from: %s to: %s" % (self.start, rr_month.start)
            self.start = rr_month.start
            
        if rr_month.end.datetime != self.end.datetime:
            print "Moving end from: %s to: %s" % (self.end, rr_month.end)
            self.end = rr_month.end
        
        #start = timerange.start
        #end = timerange.end

        #timerange = timerange

        #using a dict for easier (more intuitive) access to the days
        self.days = {}
        #print range(start.day, end.day+1)
        for i in range(self.start.day, self.end.day+1):
            day_stamp = "%s%02d%02d" % ( self.start.year, self.start.month, i )
            day = Day(day_stamp)
            self.days[i] = day
            #print i

    def _get_name(self):
        #months = [ "January"
        return self.start.strftime("%B")
    
    name = property(_get_name)
        
        
class Week(object):
    def __init__(self):
        self.days = []

class Day(Timerange):
    """
    days are a 24 hour period
    starting at midnight (00:00) and ending at 23:59...
    have a number within a month
    and a name and number within a week
    have a number within a year

    These are a time range too
    """
    def __init__(self, tstamp=None, **kwargs):
        Timerange.__init__(self, tstamp, **kwargs)

        #test to make sure we were sent an actual month,
        #rr = RelativeRange(self.start)
        rr = Timerange(self.start)
        rr_day = rr.day()
        if rr_day.start.datetime != self.start.datetime:
            #print "Moving start from: %s to: %s" % (self.start, rr_day.start)
            self.start = rr_day.start
            
        if rr_day.end.datetime != self.end.datetime:
            #print "Moving end from: %s to: %s" % (self.end, rr_day.end)
            self.end = rr_day.end

        self.number = self.start.datetime.day
        self.hours = []

        self.items = []


    ## #was tstamp_to_timerange
    ## def from_tstamp(self, text_time):
    ##     """
    ##     take a string of the format:
    ##     YYYYMMDDHHMMSS
    ##     return a tuple of python datetime objects
    ##     based on the format supplied
    ##     can assume different ranges based on the degree of accuracy

    ##     we want to assume the difference 
    ##     """
    ##     if len(text_time) == 14:
    ##         start = datetime(*(strptime(text_time, "%Y%m%d%H%M%S")[0:6]))
    ##         end = start

    ##     elif len(text_time) == 12:
    ##         start = datetime(*(strptime(text_time, "%Y%m%d%H%M")[0:6]))
    ##         delta = timedelta(minutes=1)
    ##         end = start+delta

    ##     elif len(text_time) == 10:
    ##         start = datetime(*(strptime(text_time, "%Y%m%d%H")[0:6]))
    ##         delta = timedelta(hours=1)
    ##         end = start+delta

    ##     elif len(text_time) == 8:
    ##         start = datetime(*(strptime(text_time, "%Y%m%d")[0:6]))

    ##         #this differs from RelativeRange that uses same date, 23:59:59 instead
    ##         delta = timedelta(days=1)
    ##         end = start+delta

    ##     elif len(text_time) == 6:
    ##         start = datetime(*(strptime(text_time, "%Y%m")[0:6]))
    ##         month = start.month
    ##         if month == 12:
    ##             month = 1
    ##         else:
    ##             month += 1
                
    ##         #there is no concept of months in timedelta:
    ##         #delta = timedelta(months=1)
    ##         #end = start+delta
    ##         end = datetime(start.year, month, 1)

    ##     elif len(text_time) == 4:
    ##         start = datetime(*(strptime(text_time, "%Y")[0:6]))
    ##         delta = timedelta(days=365)
    ##         end = start+delta

    ##     else:
    ##         #some other format
    ##         #start = None
    ##         #end = None
    ##         raise AttributeError, "Unknown timerange format: %s"  % text_time
        
    ##     self.start = Timestamp(start)
    ##     self.end = Timestamp(end)
    ##     return (self.start, self.end)


## #class RelativeRange(Timerange):
## class RelativeRange(object):
##     """
##     class to quickly get ranges relative to 'now'
##     sometimes these are more complex than just 'future' and 'past' on Timestamp

##     return timeranges from specific functions
##     """
##     def __init__(self, timestamp=None, name=''):
##         #Timerange.__init__(self)

##         #name should be a string indicating the type of relation
##         #e.g.
##         #last month, this month, next_month
##         self.name = name
##         if not timestamp:
##             self.ts = Timestamp()
##         else:
##             self.ts = timestamp



