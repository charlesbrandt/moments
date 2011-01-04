import sys, os

#add parent's parent directory to path to find module if not installed
sys.path.append(os.path.dirname(os.getcwd()))

#for assert_equal
from nose.tools import *

#import any needed python modules
#from datetime import datetime

#import any local modules
from moments.cycles import Timeline

class TimelineClass:
    def setUp(self):
        """
        setup up any state specific to the execution
        of the given cls.
        """
        #self.now = datetime.now()
        pass

    def test_method(self):
        # to test failure is working:
        #assert 42 == 43
        assert 42 == 42
        s = ["a", "b", "c", "d"]
        assert_equal(s, ["a", "b", "c", "d"])
        
