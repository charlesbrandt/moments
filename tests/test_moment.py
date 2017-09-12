from __future__ import print_function
from builtins import object
import sys, os
sys.path.append(os.path.dirname(os.getcwd()))

from datetime import datetime
from moments import moment, timestamp, journal

class TestMoment(object):
    def setUp(self):
        """ setup up any state specific to the execution
            of the given cls.
        """
        #self.now = datetime.now()
        self.now = timestamp.Timestamp()
        self.moment = moment.Moment(created=self.now)

    def test_render_first(self):
        first_line = "*%s \n" % self.now
        print(first_line)
        print(self.moment.render_first_line())
        assert first_line == self.moment.render_first_line()

    def test_render(self):
        first_line = "*%s \n" % self.now
        entry = first_line + self.moment.data
        print(entry)
        print(self.moment.render())
        assert entry == self.moment.render()

    def test_equal(self):

        m1 = moment.Moment(created=self.now)
        m2 = moment.Moment(created=self.now)
        #these should be different objects, that will fail equality testing:
        assert m1 != m2
        assert m1.is_equal(m2)

        later = timestamp.Timestamp(compact="20100309")
        m3 = moment.Moment(created=later)
        assert not m1.is_equal(m3)

        m2.data = "on second thought..."
        assert not m1.is_equal(m2)

        m1.data = "on second thought..."
        assert m1.is_equal(m2)
        
