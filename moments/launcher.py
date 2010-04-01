# ----------------------------------------------------------------------------
# moments
# Copyright (c) 2009-2010, Charles Brandt
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# ----------------------------------------------------------------------------
"""
# Description:
# a collection of functions to assist with launching applications

# By: Charles Brandt [code at contextiskey dot com]
# On: *2009.07.10 11:54:55 
# License:  MIT

# TODO:
# adapt this to work on other operating systems
# can check what system we're on and then run

make this callable
add a main function
pass the launch to call via command line
(maybe someday a running process like quicksilver/gnome-do)
"""
import os, sys, subprocess
from moments.helpers import load_instance

def launch(args, source='/c/instances.txt'):
    for arg in args:
        try:
            files = load_instance(source, arg)
            file_string = ' '.join(files)
            emacs(file_string)
            #echo(file_string)
            print "Loading: %s" % arg                
        except:
            print "Could not load instance: %s" % arg                

def import_pictures():
    #could just as easily import the library and call the function directly here
    command = 'python import_usb.py /media/CHARLES/DCIM/101CANON/ /media/data/graphics/incoming/'
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    return command + "\n"

## def breath():
##     command = "python /c/python/pyglet/breathe.py"
##     process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
##                                stderr=subprocess.PIPE)
##     return command + "\n"

def terminal(working_dirs=[], tabs=0):
    args = ''
    for wd in working_dirs:
        args += ' --tab --working-directory=%s' % wd
    for i in range(tabs):
        args += ' --tab'

    command = "gnome-terminal %s &" % args
    #would be better to launch this as a background process and exit the script
    #process = subprocess.Popen(command)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    #process.communicate()[0]
    return command + "\n"

def emacs(source=''):
    #print os.name
    #print sys.platform
    if sys.platform == "darwin":
        command = "/Applications/Emacs.app/Contents/MacOS/Emacs %s &" % source
    else:
        command = "emacs %s &" % source
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    #process.communicate()[0]
    return command + "\n"

def echo(source=''):
    """
    using this to attempt to find source of:
    Exception exceptions.TypeError: TypeError("'NoneType' object is not callable",) in <bound method Popen.__del__ of <subprocess.Popen object at 0xffa5d0>> ignored
    seems to only occur with shell=True
    """
    #print os.name
    #print sys.platform
    command = "echo %s" % source
    #process = subprocess.Popen(command, shell=True)
    #process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
    #                           stderr=subprocess.PIPE)
    #process = subprocess.check_call([command], {'shell':True})
    process = subprocess.check_call([command])
    #process.communicate()[0]
    return command + "\n"

def nautilus(source=''):
    command = "nautilus %s &" % source
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    return command + "\n"

def totem(movie):
    command = "totem --fullscreen %s" % (movie)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    return command + "\n"

def evolution(component="calendar"):
    #-c, --component=COMPONENT
    #    Start Evolution by activating the desired component.   COMPONENT
    #    is one of 'mail', 'calendar', 'contacts', 'tasks', 'memos'.
    command = "evolution --component=%s" % (component)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    return command + "\n"

def mount_iso(source, mount):
    if not os.path.exists(mount):
        print "creating mount point: %s" % mount
        os.mkdir(mount)

    #try unmounting first
    command = "sudo umount %s" % (mount)
    print "To unmount:"
    print command
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    output = process.communicate()[0]
    if output:
        print output
    
    
    command = "sudo mount %s %s -t iso9660 -o loop" % (source, mount)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    output = process.communicate()[0]
    if output:
        print output

def mount_iso_macosx(source):
    #http://osxdaily.com/2008/04/22/easily-mount-an-iso-in-mac-os-x/
    command = "sudo hdiutil mount %s" % (source)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    output = process.communicate()[0]
    if output:
        print output
    
def macosx_dvd(movie):
    command = "/Applications/DVD\ Player.app/Contents/MacOS/DVD\ Player &"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    return command + "\n"

def firefox(url=None, urls=[]):
    """
    be sure to pass urls in with the http:// prefix

    i.e.
    "http://www.google.com" is good
    "google.com" is not good

    http://stackoverflow.com/questions/832331/launch-a-webpage-on-a-firefox-win-tab-using-python
    Thanks Nadia!

    http://docs.python.org/library/webbrowser.html

    firefoxes "Preferences->Tab" seem to override anything done here
    """
    import webbrowser
    #print url
    if url is not None:
        webbrowser.open_new(url)
    elif urls:
        url = urls.pop(0)
        #webbrowser.open(url, new=1)
        webbrowser.open_new(url)
        for u in urls:
            webbrowser.open_new_tab(u)
    
if __name__ == '__main__':
    firefox(urls=[ "http://google.com", "http://news.google.com"])
