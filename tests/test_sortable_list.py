import sys, os

#add parent's parent directory to path to find module if not installed
sys.path.append(os.path.dirname(os.getcwd()))

#for assert_equal
from nose.tools import *

import unittest
#import any needed python modules
#from datetime import datetime

#import any local modules
from sortable_list import SortableList

class SortableListTest(unittest.TestCase):
    def setUp(self):
        """
        setup up any state specific to the execution
        of the given cls.
        """
        self.sl = SortableList()

    def test_load(self):
        # to test failure is working:
        #assert 42 == 43
        #assert 42 == 42
        #s = ["a", "b", "c", "d"]
        #assert_equal(s, ["a", "b", "c", "d"])

        self.sl.load("sample.list")
        assert len(self.sl) == 7

    def test_save(self):
        f1name = "sample.list"
        f2name = "test.txt"
        self.sl.load(f1name)
        self.sl.save(f2name)

        f1 = open(f1name)
        f1str = f1.read()
        f1.close()

        f2 = open(f2name)
        f2str = f2.read()
        f2.close()

        assert_equal(f1str, f2str)
        os.remove(f2name)
