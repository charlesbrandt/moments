import sys, os
sys.path.append(os.path.dirname(os.getcwd()))

from datetime import datetime
from moments import moment, entry, timestamp
from moments import journal #_multi as journal

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

    def test_reverse(self):
        #manually sorted in reverse:
        reversed = journal.Journal("sample_reverse.txt")
        #print dir(reversed)

        self.j.sort_entries("reverse")
        print "Pre: %s" % self.j
        #self.j.reverse()
        print "Post: %s" % self.j

        count = 0
        for e in self.j:
            assert e.is_equal(reversed[count]), "%s \n--\n%s\n\n%s" % (e.render(), reversed[count].render(), self.j.as_text())
            count += 1

    def test_from_file(self):
        j = journal.Journal()
        j.from_file("sample_log.txt")
        print self.j
        assert len(j) == 4

    def test_to_file(self):
        e = moment.Moment("test entry")
        self.j.update_entry(e)
        self.j.to_file("sample_log2.txt")
        k = journal.Journal()
        k.from_file("sample_log2.txt")
        print len(k)
        assert len(k) == 5

    def test_merge(self):
        #f1 = "sample_log.txt"
        f2 = "sample_log3.txt"
        j2 = journal.Journal()
        j2.from_file(f2)
        print j2
        assert len(j2) == 4

        self.j.from_file(f2)

        #will have 1 dupe timestamp,
        #but now dupes are added so there should be 5:
        print self.j
        assert len(self.j) == 6

    def test_merge2(self):
        f2 = "sample_log3.txt"
        self.j.from_file(f2)
        #will have 1 dupe timestamp,
        #but now dupes are added so there should be 5:
        print self.j
        assert len(self.j) == 6

    def test_entry_position(self):
        e = moment.Moment("Testing position")
        self.j.update_entry(e, position=2)
        assert self.j[2] == e
        
    def test_make_entry(self):
        data = "Testing make entry"
        self.j.make_entry(data)
        assert self.j[0].data == data
        
    def test_remove(self):
        entry = self.j[1]
        print entry.render()
        self.j.remove_entry(entry)
        assert len(self.j) == 3
        print "In dates?: %s" % self.j.dates.keys_with_item(entry)
        assert self.j.dates.keys_with_item(entry) == []
        assert self.j.tags.keys_with_item(entry) == []

    def test_limit(self):
        entries = self.j.limit(datetime(2008, 10, 21))
        print entries
        assert len(entries) == 3

        #get specific moment entry using that entry's timestamp:
        tstamp = "20081218210057"
        (start, end) = timestamp.Timerange(tstamp).as_tuple()
        print start, end
        #entries = self.j
        #assert len(entries) == 3
        entries = self.j.limit(start, end)
        assert len(entries) == 1

    def test_union(self):
        tags = [ 'foo', 'bar' ]
        entries = self.j.union_tags(tags)
        print "%s entries found from union" % len(entries)
        assert len(entries) == 3

    def test_intersect(self):
        tags = [ 'foo', 'bar' ]
        entries = self.j.intersect_tags(tags)
        print "%s entries found from intersect" % len(entries)
        assert len(entries) == 2

    def test_newest_entries_from_file(self):
        k = journal.Journal("sample_log2.txt")
        others = self.j.difference(k)
        assert len(others) == 1

        print others[0]
        print others[0].data
        assert others[0].data == "test entry\n\n"

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

