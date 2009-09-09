#*2008.06.30 14:34
#use:
#nosetests -w tests/
#if not running nose in test directory itself.

import sys, os
sys.path.append(os.path.dirname(os.getcwd()))

from moments.log import * #includes Log
from moments.entry import Entry

from datetime import datetime

class TestLog:
    def setUp(self):
        pass
    
    def test_init(self):
        #make sure log loads
        assert Log("sample_log.txt")

    def test_to_entries(self):
        #not sure if there is a good way to set this up globally
        #and still have it tested
        l = Log("sample_log.txt")
	l.from_file()
        entries = l.to_entries()
        print "ENTRIES LOADED: %s" % len(entries)
        assert len(entries) == 3

    def test_render(self):
        l = Log("./sample_log.txt")
	l.from_file()
        entries = l.to_entries()
        for e in entries:
            print e.created.strftime("%S")

    def test_save(self):
        #opening a log and saving it should yield the same file:
        l = Log("./sample_log.txt")
	l.from_file()

        entries = l.to_entries()
        l2 = Log()
        l2.name = "./sample_log4.txt"
        l2.from_entries(entries)
        l2.to_file()
        f1 = open("./sample_log.txt")
        f2 = open("./sample_log4.txt")
        lines1 = f1.readlines()
        lines2 = f2.readlines()
        print "lines in f1: %s" % len(lines1)
        print "lines in f2: %s" % len(lines2)
        assert lines1 == lines2
