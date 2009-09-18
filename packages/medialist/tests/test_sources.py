from medialist.sources import Position
#for assert_equal
from nose.tools import *

class TestPosition:
    def setUp(self):
        self.p = Position()
        
    def test_length(self):
        self.p.length = 5
        assert self.p.length == 5
        self.p.change_length(10)
        assert self.p.length == 10

