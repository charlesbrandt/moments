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
"""
import os, sys
from moments.path import Path
from moments.timestamp import Timestamp

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



class Century(object):
    def __init__(self):
        self.decades = []

class Decade(object):
    def __init__(self):
        self.years = []

class Lifetime(object):
    def __init__(self):
        self.years = []

class Year(object):
    def __init__(self):
        self.months = []

class Month(object):
    def __init__(self):
        self.days = []

class Week(object):
    def __init__(self):
        self.days = []

class Day(object):
    def __init__(self):
        self.hours = []

    

class Cycle(object):
    """
    generic object to define common characteristics of cycles

    Cycles differ from Timeranges in that they tie a period of time together
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

        #3 main distinctions to make: (thinking threes)
        #audio / movie

        #photos

        #text

        #start with one of the 3
        #and try loading brute force (everything)
        found = []

        #*2010.07.13 11:18:27
        #add some concept of priority here
        #as far as where to look first (if the locations are available)

        outgoing_root = "/c/outgoing"
        exported_root = "/media/CHARLES/outgoing"
        
        journal_root = "/c/journal"
        found.extend(self.look_in(journal_root, grouped_by="year-month"))

        personal_root = "/c/charles"


        audio_root = "/c/binaries/audio/incoming"
        found.extend(self.look_in(audio_root))

        powershot_root = "/c/binaries/graphics/incoming/daily"
        found.extend(self.look_in(powershot_root))
        slr_root = "/c/binaries/graphics/incoming/slr"
        found.extend(self.look_in(slr_root))

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

    from timestamp import Timerange, RelativeRange, Timestamp

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
    c = Cycle(last_month_r)


if __name__ == '__main__':
    main()
