import os
#for assert_equal
from nose.tools import *

from moments import sources

class TestSources:
    def setUp(self):
        a = True

    def test_converter(self):
        c = sources.Converter()
        #will take each line of an entry and make it a "source" item
        #that's why we go from 7 entries in the journal to 20 source items
        s = c.from_journal("sample_log-extract.txt")
        print len(s)
        assert len(s) == 20

