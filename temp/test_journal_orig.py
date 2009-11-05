import sys, os
sys.path.append(os.path.dirname(os.getcwd()))

from datetime import datetime
from moments import moment, entry, timestamp
from moments import journal_orig as journal

class TestJournal:
    def setUp(self):
        """ setup up any state specific to the execution
            of the given cls.
        """
        self.j = journal.Journal()
        self.j.from_file("sample_log.txt")

    def test_init(self):
        j = journal.Journal()
        j.from_file("sample_log.txt")
        assert j

    def test_from_file(self):
        j = journal.Journal()
        j.from_file("sample_log.txt")
        print "FOUND %s ENTRIES" % (len(j.entries))
        assert len(j.entries) == 3

    def test_to_file(self):
        e = moment.Moment("test entry")
        self.j.update_entry(e)
        self.j.to_file("sample_log2.txt")
        k = journal.Journal()
        k.from_file("sample_log2.txt")
        assert len(k.entries) == 4

    def test_merge(self):
        #f1 = "sample_log.txt"
        f2 = "sample_log3.txt"
        self.j.from_file(f2)

        #no longer separate merge function, just from_file again
        #self.j.merge(f2)
        
        #will have 1 dupe, so there should only be 4:
        assert len(self.j.entries) == 4

    def test_limit(self):
        entries = self.j.limit(datetime(2008, 10, 21))
        print entries
        assert len(entries) == 2

        #get specific moment entry using that entry's timestamp:
        tstamp = "20081218210057"
        (start, end) = timestamp.Timerange(tstamp).as_tuple()
        print start, end
        #entries = self.j.to_entries()
        #assert len(entries) == 3
        entries = self.j.limit(start, end)
        assert len(entries) == 1

    ## def test_to_db(self):
    ##     f2 = "sample_log3.txt"
    ##     self.j.merge(f2)
    ##     self.j.to_db()
    ##     entries = journal.session.query(entry_sa.SAEntry).all()
    ##     for e in entries:
    ##         print "%s\n%s" % (e.created, e.content)
    ##     assert len(entries) == 2, "actual length found: %s" % len(entries)

 
    ## def test_from_db(self):
    ##     j = journal.Journal()
    ##     j.from_db()
    ##     assert len(j.entries) == 1

##     def test_show_entries(self):
##         assert self.j.show_entries() == """*2008.02.25 00:35 

## dummy log file for testing Log module (and eventually others)



## """

