import sys, os, subprocess
sys.path.append(os.path.dirname(os.getcwd()))

from extract_tags import *
from moments.journal import load_journal

## def test_extract():
##     new = extract(test, "todo")
##     assert os.path.exists(new)
##     j = load_journal(new)
##     assert len(j.to_entries()) == 1
##     os.remove(new)

class TestExtracts:
    def setUp(self):
        source = "sample_log.txt"
        #make a copy
        self.test = "sample_log-copy.txt"
        cp = subprocess.Popen("cp %s %s" % (source, self.test), shell=True, stdout=subprocess.PIPE)
        cp.communicate()[0]
    
    def test_init(self):
        assert os.path.exists(self.test)

    def test_extract(self):
        new_log = extract(self.test, "todo")
        assert os.path.exists(new_log)
        j = load_journal(new_log)
        assert len(j.to_entries()) == 1
        os.remove(new_log)

    def test_extract_tags(self):
        j = load_journal(self.test)
        count = len(j.to_entries())
        extractions = [ (["todo"], "todo.txt"),
                        (["music"], "music.txt"),
                        ]
        extract_tags(self.test, extractions, save=True)

        extracted_count = 0
        for (tags, destination) in extractions:
            assert os.path.exists(destination)
            j2 = load_journal(destination)
            extracted_count += len(j2.to_entries())
            os.remove(destination)

        j = load_journal(self.test)
        count2 = len(j.to_entries())
        assert count == count2 + extracted_count, "count: %s, count2: %s, extracted: %s" % (count, count2, extracted_count)
        
    def tearDown(self):
        os.remove(self.test)
        assert not os.path.exists(self.test)
