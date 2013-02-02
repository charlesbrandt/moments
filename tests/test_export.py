import sys, os, subprocess
sys.path.append(os.path.dirname(os.getcwd()))

#for assert_equal
from nose.tools import *

from moments.journal import Journal
from moments.path import Path, load_journal
from moments import export

class TestMerge:
    ## def setUp(self):
    ##     """ setup up any state specific to the execution
    ##         of the given cls.
    ##     """
    ##     self.j = journal.Journal()
    ##     self.j.from_file("zoobar/sample_log.txt")

    def test_merge(self):
        """
        this is the manual way to merge
        there is also a function in export that wraps this up into a single call
        """
        f1 = "zoobar/sample_log.txt"
        # 2 entries in common
        f2 = "zoobar/sample_log3.txt"

        j = Journal(f1)
        len1 = len(j.entries())

        j2 = Journal(f2)
        len2 = len(j2.entries())

        j.load(f2)
        len3 = len(j.entries())

        #in this case, we know that there are two overlaping
        assert_equal(len1 + len2 - 2, len3)


class TestExport:
    def setUp(self):
        osource = "zoobar"
        #make a copy
        self.source = "zoobar-source"
        self.dest = "zoobar-dest"
        cp = subprocess.Popen("cp -r %s %s" % (osource, self.source), shell=True, stdout=subprocess.PIPE)
        cp.communicate()[0]
        mk = subprocess.Popen("mkdir %s" % (self.dest), shell=True, stdout=subprocess.PIPE)
        mk.communicate()[0]
    

    def test_export(self):
        #make a file in self.dest that will be merged automatically
        #test that the merge happened
        #d = Path(self.dest)
        original = os.path.join(self.source, "sample_log.txt")
        j = load_journal(original)
        ct1 = len(j.entries())
        
        sample = os.path.join(self.dest, "sample_log.txt")
        j = load_journal(sample, create=True)
        entry = j.make("test entry")
        assert len(j.entries()) == 1
        j.save(sample)
        export.export_logs(self.source, self.dest)

        j = load_journal(sample)
        ct2 = len(j.entries())

        assert ct1 + 1 == ct2

    def tearDown(self):
        rm1 = subprocess.Popen("rm -r %s" % (self.source), shell=True, stdout=subprocess.PIPE)
        rm1.communicate()[0]

        rm2 = subprocess.Popen("rm -r %s" % (self.dest), shell=True, stdout=subprocess.PIPE)
        rm2.communicate()[0]

        assert not os.path.exists(self.source)
        assert not os.path.exists(self.dest)
