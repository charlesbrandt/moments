import os

from osbrowser.node import Node
#for assert_equal
from nose.tools import *

class TestNode:
    def setUp(self):
        self.node = Node(os.path.join(os.getcwd(), "IMG_6166_l.JPG"))

    def test_name(self):
        assert str(self.node) == os.path.join(os.getcwd(), "IMG_6166_l.JPG")
        
                       
