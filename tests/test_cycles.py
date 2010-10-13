import sys, os
sys.path.append(os.path.dirname(os.getcwd()))

from datetime import datetime
from moments import moment, entry, timestamp
from moments import cycles

class TestMonth:
    def setUp(self):
        """ setup up any state specific to the execution
            of the given cls.
        """
        pass

    def test_init(self):
        tstamp = "20101001-201010312359"
        #tr = timestamp.Timerange(tstamp)
        
        m = cycles.Month(tstamp)

        tstamp = "20101001"
        m2 = cycles.Month(tstamp)
        assert True == False

