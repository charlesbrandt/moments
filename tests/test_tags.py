import sys, os
sys.path.append(os.path.dirname(os.getcwd()))

#for assert_equal
from nose.tools import *

from moments.tags import *

def test_tag():
    s = to_tag("HELLo tAG")
    #assert s == "hello_tag", s
    assert_equal (s, "hello_tag")

    s = from_tag(s)
    assert_equal (s, "Hello Tag")

class TestTags:
    def setUp(self):
        self.tags = Tags(['tag1', 'tag2'])
        self.tags2 = Tags(['tag2', 'tag1'])
        
    def test_init(self):
        #make sure it loads
        assert self.tags

    def test_string(self):
        #test that str(Tags) == "tag1 tag2"
        assert str(self.tags) == "tag1 tag2"

    def test_tagstring(self):
        assert self.tags.to_tag_string() == "tag1-tag2"

    def test_repr(self):
        assert repr(self.tags) == "['tag1', 'tag2']"

    def test_empty(self):
        self.empty = Tags()
        assert self.empty == []
        assert str(self.empty) == ''

    def test_assignment(self):
        a = "blahblah"
        b =  Tags().from_tag_string(a)
        assert b == ['blahblah']

    def test_equal(self):
        assert self.tags != self.tags2
        assert self.tags.is_equal(self.tags2)
