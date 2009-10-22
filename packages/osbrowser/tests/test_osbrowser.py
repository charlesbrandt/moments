import os, sys
sys.path.append(os.path.dirname(os.getcwd()))

from osbrowser.meta import make_node
from osbrowser import shell, node, image

#for assert_equal
from nose.tools import *

def test_ls():
    """
    looks like python sort and ls sort files with '~' differently.
    best to just remove those for now.

    not just those though, also files with capitalized letters
    python puts those before all lower case
    looks like ls sorts case agnostic
    """
    
    path = './'
    #http://www.python.org/doc/current/lib/os-process.html
    a = os.popen('ls -a %s' % path)
    b = shell.ls('./')
    #ls -a adds . and ..
    b = '.\n..\n' + b
    #assert a.read() == b
    assert_equal(a.read(), b)
    
def test_osbrowser_get_images():
    path = '.'
    d = node.Directory(path)

    d.scan_filetypes()
    images = []
    for i in d.images:
        images.append(str(i))

    #special case for local path
    cmd = os.popen('ls *.JPG')
    #cmd = os.popen('ls %s/*.JPG' % path)
    res = cmd.read()
    images2 = res.split('\n')
    #last new line in ls output adds an empty item to list
    images2 = images2[:-1]

    print images
    print images2

    assert images == images2

def test_image_size_name():
    i = image.Image('./IMG_6166_l.JPG')
    new_name = i.size_name('small')
    assert new_name == 'IMG_6166_l_s.JPG'

def test_image_get_size():
    i = image.Image('./IMG_6166_l.JPG')

    path = i.get_size('small')
    #print path
    assert path == 'sized/small/IMG_6166_l_s.JPG'
