import sys, os
sys.path.append(os.path.dirname(os.getcwd()))

#for assert_equal
from nose.tools import *

from moments.path import *

class TestPath:
    """
    see also test node
    """
    def setUp(self):
        self.path = Path("a/b/c/d.txt")
        
    def test_init(self):
        #make sure it loads
        assert self.path

    def test_path_to_tag(self):
        #s = path_to_tags("a/b/c/d.txt")
        s = self.path.to_tags()
        
        #assert s == "hello_tag", s
        assert_equal (s, ["a", "b", "c", "d"])

        s = Path("/d/e/f.g.txt").to_tags()
        assert_equal (s, ["d", "e", "f.g"])

        #s = path_to_tags("/h/i/j/k/")
        s = Path("/h/i/j/k/").to_tags()
        assert_equal (s, ["h", "i", "j", "k"])

    def test_create(self):
        p = "create_me.txt"
        path = Path(p)
        assert not os.path.exists(p)
        path.create()
        assert os.path.exists(p)
        path.remove()
        assert not os.path.exists(p)
        
