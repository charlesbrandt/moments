import sys, os
sys.path.append(os.path.dirname(os.getcwd()))
#print sys.path

from datetime import datetime
from moments import moment, timestamp
from moments import journal 

class TestJournal:
    def setUp(self):
        """
        setup up any state specific to the execution
        of the given cls.
        """
        self.j = journal.Journal()
        self.j.load("zoobar/sample_log.txt")

    def test_init(self):
        j = journal.Journal()
        j.load("zoobar/sample_log.txt")
        assert j

    def test_reverse(self):
        #manually sorted in reverse:
        reversed = journal.Journal("zoobar/sample_reverse.txt")
        #print dir(reversed)

        self.j.sort("reverse")
        print "Pre: %s" % self.j
        #self.j.reverse()
        print "Post: %s" % self.j

        count = 0
        for e in self.j.entries():
            assert e.is_equal(reversed.entry(count)), "Not the same: %s \n--\n%s\n\n%s" % (e.render(), reversed[count].render(), self.j.as_text())
            count += 1

    def test_load(self):
        j = journal.Journal()
        j.load("zoobar/sample_log.txt")
        print self.j
        assert len(j.entries()) == 4

    def test_save(self):
        e = moment.Moment("test entry", now=True)
        self.j.update(e)
        self.j.save("zoobar/sample_log2.txt")
        k = journal.Journal()
        k.load("zoobar/sample_log2.txt")
        print len(k.entries())
        assert len(k.entries()) == 5

        
    def test_update(self):
        """
        test for known duplicate entries
        """
        self.j.debug = True
        print "All entries: " 
        for e in self.j.entries():
            print e.as_dict()
        pre_len = len(self.j.entries())
        e = moment.Moment(tags=[u'foo'], data=u'another test entry, this one has seconds\n\n', created='2008.10.22 11:15:42')
        self.j.update(e)
        post_len = len(self.j.entries())
        print "pre: %s, post: %s" % (pre_len, post_len)
        assert pre_len == post_len
        #assert True == False

    def test_merge(self):
        #f1 = "sample_log.txt"
        f2 = "zoobar/sample_log3.txt"
        j2 = journal.Journal()
        j2.load(f2)
        print j2
        print len(j2.entries())
        assert len(j2.entries()) == 4

        print "pre: %s" % len(self.j.entries())
        self.j.load(f2)

        #will have 1 dupe timestamp,
        #but now dupes are added so there should be 5:
        print self.j
        assert len(self.j.entries()) == 6

    def test_merge2(self):
        f2 = "zoobar/sample_log3.txt"
        self.j.load(f2)
        #will have 1 dupe timestamp,
        #but now dupes are added so there should be 5:
        print self.j
        for e in self.j.entries():
            print e.render()
            
        print len(self.j.entries())
        assert len(self.j.entries()) == 6

    def test_date(self):
        ts = timestamp.Timestamp(compact="20081218210057")
        result = self.j.date(ts)
        #assert result.has_key(ts.compact())
        #assert len(result[ts.compact()]) == 1
        #assert result.has_key(ts.compact())
        print "Result: %s" % result
        assert len(result) == 1
        
    def test_tag(self):
        tag = "foo"
        result = self.j.tag(tag)
        #assert result.has_key(tag)
        #assert len(result[tag]) == 3
        print result
        assert len(result) == 3

    def test_entry_position(self):
        es = self.j.entries()
        for e in es:
            print e.render()

        print "xxxxxxxxxxxxxxxxxxxxxxxxx"
        new_e = moment.Moment("Testing position", now=True)
        self.j.update(new_e, position=2)

        es = self.j.entries()
        for e in es:
            print e.render()
        print "xxxxxxxxxxxxxxxxxxxxxxxxx"

        #with remote journal, might not be the same entry object
        #but might still be equivalent
        #assert self.j.entry(2) == e
        print "ENTRY1: ->%s<-" % self.j.entry(2).render()
        print "ENTRY2: ->%s<-" % new_e.render()
        assert self.j.entry(2).is_equal(new_e)
        
    def test_make_entry(self):
        data = "Testing make entry"
        self.j.make(data)
        assert self.j.entry(0).data == data
        
    def test_search(self):
        """search for matching tags"""
        results = self.j.search("foo")
        print results
        #should only be one matching tag
        assert results == ['foo']
        
    def test_remove(self):
        entry = self.j.entry(1)
        print entry.render()
        self.j.remove(entry)
        print len(self.j.entries())
        assert len(self.j.entries()) == 3
        #TODO:
        #not sure if we should be referencing hidden attributes in tests
        print "In dates?: %s" % self.j._dates.keys_with_item(entry)
        assert self.j._dates.keys_with_item(entry) == []
        assert self.j._tags.keys_with_item(entry) == []

    def test_range(self):
        entries = self.j.range(datetime(2008, 10, 21))
        print entries
        assert len(entries) == 3

        #get specific moment entry using that entry's timestamp:
        tstamp = "20081218210057"
        #this goes to now due to second level accuracy of tstamp:
        #(start, end) = timestamp.Timerange(tstamp).as_tuple()
        #print start, end
        tstamp = "20081218210057-20081218210059"
        (start, end) = timestamp.Timerange(tstamp).as_tuple()
        print start, end
        #entries = self.j
        #assert len(entries) == 3
        entries = self.j.range(start, end)
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


class TestRemoteJournal(TestJournal):
    def setUp(self):
        """
        setup up any state specific to the execution
        of the given cls.
        """
        print "Be sure local server is running"
        print "cd /c/moments/moments"
        print "python server.py /c/moments/tests/"
        self.j = journal.RemoteJournal('http://localhost:8000')
        #be sure we're back to a clean slate:
        self.j.clear()
        self.j.load("zoobar/sample_log.txt")
        #print os.curdir
        #f = open('zoobar/sample_log.txt')
        #print f.read()
        print "Number of entries after load: %s" % len(self.j.entries())

    def test_clear(self):
        """
        this doesn't really matter in a local instance test
        but with a server, the loaded journal entries
        are not cleared automatically by just instantiating a new RemoteJournal
        """
        print len(self.j.entries())
        self.j.clear()
        print len(self.j.entries())
        assert len(self.j.entries()) == 0

    def test_remove(self):
        """
        test_remove: this differs from local journal tests
        have access to _dates and _tags associations there
        we don't have access to those in a remote journal

        can't test that level, but can test that something was removed.
        
        run this first...
        in the case of a server, entries are persistent
        so previously loaded items remain

        not sure that order can be forced
        """
        print len(self.j.entries())

        #self.j.clear()
        entry = self.j.entry(1)
        print entry.render()
        self.j.remove(entry)
        print len(self.j.entries())
        assert len(self.j.entries()) == 3

