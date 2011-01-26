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
*2010.05.13 17:52:29
new module to define commonly occuring cycles of time

cycles, or periods, can be used to collect various moments together
and provide meta level information for the collection
more than a journal, since it can contain references to other files as well
like pictures, audio, and movies.

also not to be confused with a timestamp, which is essentially just a string representation of a specific time

this is a collection of information over a range of time

consider this making a directory structure for time
each level of the structure has it's own type of object
that understands how to summarize lower level objects it contains.

see also
*2007.12.11 10:24 c journal 2007 12 20071211 private meta original

see also:
/c/moments/moments/scripts/launch.py
for check calendar...
some idea of loading a month file there
"""
import os, sys
from moments.path import Path
#from moments.timestamp import Timestamp
from timestamp import Timerange, RelativeRange, Timestamp

class Timeline(object):
    """
    *2010.12.30 18:04:04
    moving into cycles...
    similar ideas here.
    
    #2010.12.15 18:46:06
    also [2010.12.19 11:41:55] 
    combining with mindstream

    take a loaded journal (or journal subset)
    index based on various cycles

    allow easy formatting

    (do not worry about loading here)

    very similar to path.directory functionality
    and pose functionality
    """
    def __init__(self, journal, media='/c/binaries/journal'):
        """
        """
        self.j = journal

    def render_year(self, year=None):
        #if no year, use current year

        #look for all entries in this year

        #use the static image for the header
        #or, if no static, look for most popular image in this year

        #show all days for current month (summarize each day)

        #show highlights only for two previous months for current year (not current month)

        #show 3x3 grid of remaining months

        #show grid for previous years
        pass


#seems that Cycles and TimeRanges are really equivalent
class TimeCollection(object):
    """
    generic object to define common characteristics of cycles

    TimeCollections differ from Timeranges in that they tie a period of time together
    with some files and data associated with that time

        #once this is working, should be easier to extract things like
        #cwt, bundles, dwt, etc
        #can then leave everything in tact as timeline.
        
        #if directory sorted by [ days, months, years ], only load relevant

        #ideally:
        #look.in(path).for([files, entries]).ordered_by(time, tag, unknown)

        #or maybe just:
        #look_in(path, for="files", order_by="time")

    """
    def __init__(self, timerange):
        self.parts = []
        #the bounds of the cycle
        self.timerange = timerange

        #print self.timerange
        #load sources of information for this cycle:
        #this is related to search... how it looks in different sources
        #also similar to player or thumbnails...
        #how it will load a directory differently depending on 
        #if the directory contains journals or just binary files

        #can be smart about what we load
        #if the directory structure is organized by time
        #automatically navigate to the range specified in our cycle
        #(rather than loading everything brute force
        # and limiting the journal later)

        found = []

        #3 main distinctions to make: (thinking threes)
        #text

        #*2010.07.13 11:18:27
        #add some concept of priority here
        #as far as where to look first (if the locations are available)

        outgoing_root = "/c/outgoing"
        exported_root = "/media/CHARLES/outgoing"
        
        journal_root = "/c/journal"
        found.extend(self.look_in(journal_root, grouped_by="year-month"))

        personal_root = "/c/charles"
        #can optionally add and load other sources of journals here
        #other repositories.

        #photos
        powershot_root = "/c/binaries/graphics/incoming/daily"
        found.extend(self.look_in(powershot_root))
        slr_root = "/c/binaries/graphics/incoming/slr"
        found.extend(self.look_in(slr_root))

        #audio / movie
        audio_root = "/c/binaries/audio/incoming"
        found.extend(self.look_in(audio_root))

        print "FOUND:"
        for p in found:
            print p

        #found should now hold a list of directories
        #that should hold content relevant to the range initialized
        
        #still need to go through those files and do the right thing

        #if they're text files, load as a journal
        #if they're binary files, make a new journal entry based on timestamp
        #could also look for any entries associated with binary files
        #in order to get tags associated with those files.


        

    def load_year(self, year, paths):
        """
        helper function for look_in
        when dealing with year directories to recurse into
        """
        start = self.timerange.start
        end = self.timerange.end
        matches = []

        year_path = ""
        for p in paths:
            path = Path(p)
            if path.name == str(year):
                year_path = path

        if year_path:
            if year == start.year:
                start_month = start.month
            else:
                start_month = 1

            if year == end.year:
                end_month = end.month
            else:
                end_month = 12

            year_dir = year_path.load()
            for m in range(start_month, end_month+1):
                #matches.extend(load_month(m,
                month = "%02d" % m
                month_path = os.path.join(str(year_path), month)
                if os.path.exists(month_path):
                    matches.append(month_path)
                else:
                    print "not found: %s" % month_path
            
        return matches
    
    def look_in(self, path, look_for="files", grouped_by="day",
                order_by="time"):
        """
        grouped_by describes how the (sub) files are stored in the path
        sometimes items are collected by day
        other times they are collected by year/month/day
        """
        found = []
        p = Path(path)
        if p.type() == "Directory":
            d = p.load()
            if grouped_by == "day":
                for sub_path in d.sub_paths:
                    sp = Path(sub_path)
                    parts = sp.name.split('-')
                    #print parts[0]
                    try:
                        start = Timestamp(compact=parts[0])
                        #print start
                    except:
                        print "could not parse %s" % parts[0]
                        start = None

                    if start is not None:
                        #print start
                        if start.is_in(self.timerange):
                            found.append(sp)
                        #print "%s in %s" % (start, self.timerange)
                    else:
                        #print "%s NOT in %s" % (start, self.timerange)
                        pass
            elif grouped_by == "year-month":
                start_year = self.timerange.start.year
                end_year = self.timerange.end.year
                #end_month = self.timerange.end.month
                #start_month = self.timerange.start.month
                if start_year != end_year:
                    for year in range(start_year, end_year+1):
                        found.extend(self.load_year(year, d.sub_paths))
                else:
                    print "Start: %s" % start_year
                    print "Paths: %s" % d.sub_paths
                    found.extend(self.load_year(start_year, d.sub_paths))
                        
        return found
        
    def check(self):
        this_month = ''
        if self.overlaps(this_month):
            print "Warning: may not be able to find all entries until month is consolidated"

        
    def overlaps(other):
        """
        check to see if any of our parts overlap with the other cycle's parts
        """
        overlap = False
        for p in self.parts:
            if p in other.parts:
                overlap = True

        return overlap

class Lifetime(object):
    def __init__(self):
        self.years = []

class Century(object):
    def __init__(self):
        self.decades = []

class Decade(object):
    def __init__(self):
        self.years = []

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
        rr = RelativeRange(self.start)
        rr_month = rr.month()
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
        rr = RelativeRange(self.start)
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


#relative cycles
class Measure(object):
    def __init__(self):
        self.beats = []

class Tempo(object):
    pass

class Sequence(object):
    """ collection of tracks """
    def __init__(self):
        self.tracks = []
        self.timing = "relative" # for tempo base or "fixed" for seconds

def main():
    if len(sys.argv) > 1:
        helps = ['--help', 'help', '-h']
        for i in helps:
            if i in sys.argv:
                usage()
                exit()
        #skip the first argument (filename):
        #for arg in sys.argv[1:]:
        #    try:
        #        files = load_instance("/c/charles/instances.txt", arg)


    timerange = Timerange('20100428-20100528')
    #dec = Timestamp(compact='201012')
    #feb = Timestamp(compact='201002')
    #dec_r = rr.month(dec)
    #feb_r = rr.month(feb)

    rr = RelativeRange()
    rr.week()

    this_month_r = rr.this_month()
    last_month_r = rr.last_month()

    print last_month_r
    c = TimeCollection(last_month_r)


if __name__ == '__main__':
    main()
