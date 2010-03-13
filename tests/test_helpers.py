import sys, os, subprocess
sys.path.append(os.path.dirname(os.getcwd()))

from moments.helpers import *

class TestHelpers:
    #def setUp(self):
    #    pass

    def test_today(self):
        """
        this at least calls the helper and makes sure that a file is created
        doesn't check for anything else yet.
        """
        now = Timestamp()
        assemble_today(destination='./')
        tfile = './%s' % now.filename()
        print tfile
        assert os.path.exists(tfile)
        os.remove(tfile)
