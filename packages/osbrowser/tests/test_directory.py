import os

from osbrowser.node import Directory
#for assert_equal
from nose.tools import *

class TestDirectory:
    def setUp(self):
        self.d = Directory(os.getcwd())

    #*2009.01.26 15:14:53
    #commenting out until tests are not dependent on file timestamps staying
    #the same
    #should be set by the test to a known date before testing
    ## def test_file_date_range(self):
    ##     #print self.d.file_date_range()
    ##     #this works for now, will break when a file is updated.
    ##     print self.d.file_date_range()
    ##     assert self.d.file_date_range() == "20090121-20090122"
    ##     #might be abled to use sized directory for better reliability:
    ##     #but no files, only sub-directories...
    ##     #create a new test directory
    ##     new_d = Directory(os.path.join(os.getcwd(), "zoobar"))
    ##     print new_d.file_date_range()
    ##     assert new_d.file_date_range() == "20090121"
