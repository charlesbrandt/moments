from __future__ import print_function
from builtins import object
import sys, os, subprocess
sys.path.append(os.path.dirname(os.getcwd()))

#from extract_tags import *
from moments.filters import extract_tags, extract_many, omit_date_tags
from moments.path import load_journal

## def test_extract():
##     new = extract(test, "todo")
##     assert os.path.exists(new)
##     j = load_journal(new)
##     assert len(j) == 1
##     os.remove(new)

class TestExtracts(object):
    def setUp(self):
        source = "zoobar/extractable_log.txt"
        #make a copy
        self.test = "zoobar/sample_log-copy.txt"
        cp = subprocess.Popen("cp %s %s" % (source, self.test), shell=True, stdout=subprocess.PIPE)
        cp.communicate()[0]
        
        self.extractions = [ (["todo"], "zoobar/todo.txt"),
                             (["music"], "zoobar/music.txt"),
                             ]

        j = load_journal(self.test)
        self.original_count = len(j.entries())

    def test_init(self):
        assert os.path.exists(self.test)

    def test_omit_date_tags(self):
        tags = [ "20110915", "2011", "09", "tag_to_keep"]
        new_tags = omit_date_tags(tags)
        print(new_tags)
        assert new_tags == [ "tag_to_keep" ]
        
        
    #makes assumtions about where log will be created
    #this is no longer the case
    #def test_extract(self):
    #    new_log = extract(self.test, "todo")
    #    assert os.path.exists(new_log)
    #    j = load_journal(new_log)
    #    assert len(j) == 1
    #    os.remove(new_log)

    def test_extract_tags(self):
        """
        this test mimics the functionality of extract_many
        """

        extract_tags(self.test, self.extractions, save=True)

        extracted_count = 0
        for (tags, destination) in self.extractions:
            #touch = subprocess.Popen("touch %s" % (destination), shell=True, stdout=subprocess.PIPE)
            #touch.communicate()[0]
            #assert os.path.exists(destination)
            j2 = load_journal(destination, create=True)
            extracted_count += len(j2.entries())
            os.remove(destination)

        j = load_journal(self.test)
        count2 = len(j.entries())
        assert self.original_count == count2 + extracted_count, "count: %s, count2: %s, extracted: %s" % (self.original_count, count2, extracted_count)

    def test_extract_many(self):
        extract_many(self.test, self.extractions, save=True)

        extracted_count = 0
        for (tags, destination) in self.extractions:
            #touch = subprocess.Popen("touch %s" % (destination), shell=True, stdout=subprocess.PIPE)
            #touch.communicate()[0]
            #assert os.path.exists(destination)
            j2 = load_journal(destination, create=True)
            extracted_count += len(j2.entries())
            os.remove(destination)

        j = load_journal(self.test)
        count2 = len(j.entries())
        assert self.original_count == count2 + extracted_count, "count: %s, count2: %s, extracted: %s" % (self.original_count, count2, extracted_count)
        
    def tearDown(self):
        os.remove(self.test)
        assert not os.path.exists(self.test)
