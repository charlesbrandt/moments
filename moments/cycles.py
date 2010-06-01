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
    """
    def __init__(self, timerange):
        self.parts = []
        #the bounds of the cycle
        self.timerange = timerange
    
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
        audio_root = "/c/binaries/audio"

        #ideally:
        #look.in(path).for([files, entries]).ordered_by(time, tag, unknown)
        
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
    dec = Timestamp(compact='201012')
    feb = Timestamp(compact='201002')
    rr = RelativeRange()
    this_month_r = rr.this_month()
    dec_r = rr.month(dec)
    feb_r = rr.month(feb)

    print this_month_r
    rr.week()

if __name__ == '__main__':
    main()
