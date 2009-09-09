from quotes import Quotes
#for assert_equal
from nose.tools import *

class TestQuotes:
    def setUp(self):
        self.s = Quotes()

    def test_init(self):
        assert self.s

    def test_lookup(self):
        result = self.s.lookup_quote('4.34')
        #print "->", result, "<-"
        assert result == """4.34. Thus, the supreme state of Independence manifests while the gunas reabsorb themselves into Prakriti, having no more purpose to serve the Purusha. Or, to look from another angle, the power of pure consciousness settles in its own pure nature. 
So concludes the Sutras of Book Four 
"""

    def test_next(self):
        self.s.quotes.cur_pos = 0
        pos1 = self.s.quotes.cur_pos
        n = self.s.next()
        pos2 = self.s.quotes.cur_pos
        assert pos1 == pos2-1

        print "POS1: %s" % pos1
        print "POS2: %s" % pos2
        print "first quote: %s" % n
        print "quote at pos2: %s" % self.s.quotes.jump_to_num(pos2)
        
        assert n == self.s.to_html(self.s.quotes.jump_to_num(pos2))
