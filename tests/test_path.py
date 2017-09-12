from __future__ import print_function
from builtins import str
from builtins import object
import sys, os
sys.path.append(os.path.dirname(os.getcwd()))

#for assert_equal
from nose.tools import *

from moments.timestamp import Timestamp
from moments.path import File, Directory, Image, Path, name_only, load_instance

class TestStorage(object):
    def setUp(self):
        self.node = File(os.path.join(os.getcwd(), "zoobar/IMG_6166_l.JPG"))

    def test_name(self):
        assert str(self.node.path) == os.path.join(os.getcwd(), "zoobar/IMG_6166_l.JPG")
        assert str(self.node) == "IMG_6166_l.JPG"

    def test_load_instance(self):
        items = load_instance('zoobar/instances.txt', 'tests')
        print(items)
        assert len(items) == 3

    def test_change(self):
        print("THIS WILL FAIL ON MAC OSX.  NO SUPPORT FOR os.utime")
        print("others may need to run twice to get times set as expected")
        now = Timestamp()
        #this does not work as expected:
        #atime = Timestamp().from_epoch(self.node.atime)
        atime = Timestamp()
        atime.from_epoch(self.node.atime)
        mtime = Timestamp()
        mtime.from_epoch(self.node.mtime)

        assert str(mtime) != str(now)
        assert str(atime) != str(now)
        print("Current atime: %s" % atime)
        print("Current mtime: %s" % mtime)
        print("POSIX FORMATS:")
        print("New atime: %s" % now.epoch())
        print("Current atime: %s" % self.node.atime)
        print("Current mtime: %s" % self.node.mtime)
        self.node.change_stats(now, now)

        #regenerate updates:
        atime = Timestamp()
        atime.from_epoch(self.node.atime)
        mtime = Timestamp()
        mtime.from_epoch(self.node.mtime)
        assert str(mtime) == str(now)
        assert str(atime) == str(now)

# deprecated
## def test_image_size_name():
##     i = Image('zoobar/IMG_6166_l.JPG')
##     new_name = i.size_name('small')
##     assert_equal(new_name, 'IMG_6166_l_s.JPG')

def test_image_get_size():
    i = Image('./zoobar/IMG_6166_l.JPG')

    path = i.size_path('small', square=False)
    #print path
    assert_equal(str(path), os.path.abspath('./zoobar/sized/small/IMG_6166_l_s.JPG'))


class TestDirectory(object):
    def setUp(self):
        #self.d = Directory(os.getcwd())
        path = './zoobar'
        self.d = Directory(path)

    def test_files_to_journal(self):
        output = "temp_files_to_journal_test_output.txt"
        self.d.files_to_journal(journal_file=output)
        dest = os.path.join('./zoobar', output)
        assert os.path.exists(dest)
        path = Path(dest)
        path.remove()
        assert not os.path.exists(dest)

    def test_sortable_list_name(self):
        destination = self.d.sortable_list_path()
        print(destination)
        #assert False
        assert destination == "./zoobar/zoobar.list"
        
    def test_default_image(self):
        d2 = Directory("./zoobar")
        print(d2.images)
        print(d2.default_image())
        print(d2.images)
        
        d = Directory(os.getcwd())
        assert d.default_image() == None

        #assert False

    def test_get_images(self):
        path = './zoobar'
        d = Directory(path)

        d.scan_filetypes()
        images = []
        for i in d.images:
            images.append(str(i.parent().filename) + '/' + str(i.filename))

        #special case for local path
        cmd = os.popen('ls zoobar/*.JPG')
        #cmd = os.popen('ls %s/*.JPG' % path)
        result = cmd.read()
        images2 = result.split('\n')
        #last new line in ls output adds an empty item to list
        images2 = images2[:-1]

        print(images)
        print(images2)

        assert images == images2

    def test_make_thumbs(self):
        path = Path('./zoobar/sized')
        path.remove()
        self.d.make_thumbs()
        #assert False

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

class TestPath(object):
    """
    see also test node
    """
    def setUp(self):
        self.path = Path("/a/b/c/d.txt")
        
    def test_init(self):
        #make sure it loads
        assert self.path

    def test_periods(self):
        name = ".emacs.desktop"
        p = Path(name)
        print(name_only(name))
        print(str(p))
        assert name == str(p)
        

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

    def test_hidden(self):
        path_s = "zoobar/.emacs"
        hidden = Path(path_s)
        print(str(hidden))
        print("Filename: %s (name: %s, extension: %s)" % (hidden.filename, hidden.name, hidden.extension))
        assert hidden._full_name == ".emacs"
        #assert name_only(path_s)
        assert hidden.filename == ".emacs"
        assert str(hidden) == path_s

    def test_load_journal(self):
        dest = 'zoobar/todo.txt'
        p = Path(dest)
        p.load_journal(create=True)
        assert os.path.exists(dest)
        p.remove()
        assert not os.path.exists(dest)
        
    def test_create(self):
        p = "create_me.txt"
        path = Path(p)
        assert not os.path.exists(p)
        path.create()
        assert os.path.exists(p)
        path.remove()
        assert not os.path.exists(p)
        
