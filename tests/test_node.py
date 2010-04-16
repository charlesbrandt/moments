import os

#for assert_equal
from nose.tools import *

import moments.path
from moments.timestamp import Timestamp

class TestStorage:
    def setUp(self):
        self.node = moments.path.File(os.path.join(os.getcwd(), "IMG_6166_l.JPG"))

    def test_name(self):
        assert str(self.node.path) == os.path.join(os.getcwd(), "IMG_6166_l.JPG")
        assert str(self.node) == "IMG_6166_l.JPG"

    def test_change(self):
        print "THIS WILL FAIL ON MAC OSX.  NO SUPPORT FOR os.utime"
        now = Timestamp()
        #this does not work as expected:
        #atime = Timestamp().from_epoch(self.node.atime)
        atime = Timestamp()
        atime.from_epoch(self.node.atime)
        mtime = Timestamp()
        mtime.from_epoch(self.node.mtime)

        assert str(mtime) != str(now)
        assert str(atime) != str(now)
        print "Current atime: %s" % atime
        print "Current mtime: %s" % mtime
        print "POSIX FORMATS:"
        print "New atime: %s" % now.epoch()
        print "Current atime: %s" % self.node.atime
        print "Current mtime: %s" % self.node.mtime
        self.node.change_stats(now, now)

        #regenerate updates:
        atime = Timestamp()
        atime.from_epoch(self.node.atime)
        mtime = Timestamp()
        mtime.from_epoch(self.node.mtime)
        assert str(mtime) == str(now)
        assert str(atime) == str(now)

            
def test_osbrowser_get_images():
    path = '.'
    d = moments.path.Directory(path)

    d.scan_filetypes()
    images = []
    for i in d.images:
        images.append(str(i))

    #special case for local path
    cmd = os.popen('ls *.JPG')
    #cmd = os.popen('ls %s/*.JPG' % path)
    result = cmd.read()
    images2 = result.split('\n')
    #last new line in ls output adds an empty item to list
    images2 = images2[:-1]

    print images
    print images2

    assert images == images2

def test_image_size_name():
    i = moments.path.Image('./IMG_6166_l.JPG')
    new_name = i.size_name('small')
    assert_equal(new_name, 'IMG_6166_l_s.JPG')

def test_image_get_size():
    i = moments.path.Image('./IMG_6166_l.JPG')

    path = i.get_size('small')
    #print path
    assert_equal(path, os.path.abspath('./sized/small/IMG_6166_l_s.JPG'))

from moments.path import Directory
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
