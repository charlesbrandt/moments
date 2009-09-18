from medialist.medialist import MediaList
#for assert_equal
from nose.tools import *

class TestMediaList:
    def setUp(self):
        m = MediaList()
        m.append('a')
        m.append('c')
        m.append('d')
        m.append('b')
        self.m = m
        
    def test_init(self):
        assert len(self.m) == 4

    def test_sort(self):
        self.m.sort_items()
        assert self.m == ['a', 'b', 'c', 'd']

    def test_reverse(self):
        self.m.sort_order = "reverse"
        self.m.sort_items()
        assert self.m == ['d', 'c', 'b', 'a']

    def test_random(self):
        self.m.sort_order = "random"
        self.m.sort_items()
        assert self.m == ['a', 'c', 'd', 'b']

    def test_jump(self):
        #*2009.03.25 14:20:09
        #changing assumtion to list positions starting at 0
        assert self.m.jump_to_num(2) == 'd'
