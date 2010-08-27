import os
#for assert_equal
from nose.tools import *

from moments import sources

class TestSources:
    def setUp(self):
        a = True
        self.c = sources.Converter()

    def test_converter(self):
        #will take each line of an entry and make it a "source" item
        #that's why we go from 7 entries in the journal to 20 source items
        s = self.c.from_journal("sample_log-extract.txt")
        print len(s)
        assert len(s) == 20

    def test_m3u(self):
        s = self.c.from_m3u("sample.m3u")
        print len(s)
        m3u = self.c.to_m3u(s, verify=False)
        f = open("temp.m3u", 'w')
        f.write(m3u)
        f.close()
        assert True == False
        
        
        
