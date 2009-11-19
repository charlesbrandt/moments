import sys, os
sys.path.append(os.path.dirname(os.getcwd()))

from datetime import datetime
from moments import moment, entry, timestamp, journal

class TestMoment:
    def setUp(self):
        """ setup up any state specific to the execution
            of the given cls.
        """
        #self.now = datetime.now()
        self.now = timestamp.Timestamp()
        self.moment = moment.Moment(created=self.now)

    def test_render_first(self):
        first_line = "*%s \n" % self.now
        print first_line
        print self.moment.render_first_line()
        assert first_line == self.moment.render_first_line()

    def test_render(self):
        first_line = "*%s \n" % self.now
        entry = first_line + self.moment.data
        print entry
        print self.moment.render()
        assert entry == self.moment.render()
