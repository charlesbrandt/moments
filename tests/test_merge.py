import sys, os
sys.path.append(os.path.dirname(os.getcwd()))

#for assert_equal
from nose.tools import *

from scripts import merge_logs
from moments.journal import Journal

class TestJournal:
    ## def setUp(self):
    ##     """ setup up any state specific to the execution
    ##         of the given cls.
    ##     """
    ##     self.j = journal.Journal()
    ##     self.j.from_file("zoobar/sample_log.txt")

    def test_merge(self):
        f1 = "zoobar/sample_log.txt"
        # 2 entries in common
        f2 = "zoobar/sample_log3.txt"

        j = Journal(f1)
        len1 = len(j)

        j2 = Journal(f2)
        len2 = len(j2)


        j.from_file(f2)
        len3 = len(j)

        #in this case, we know that there are two overlaping
        assert_equal(len1 + len2 - 2, len3)
