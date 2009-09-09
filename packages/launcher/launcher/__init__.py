#
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
import os, subprocess

def import_pictures():
    #could just as easily import the library and call the function directly here
    command = 'python import_usb.py /media/CHARLES/DCIM/101CANON/ /media/data/graphics/incoming/'
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    return command + "\n"

def breath():
    command = "python /c/python/pyglet/breathe.py"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    return command + "\n"

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
    command = "emacs %s &" % source
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
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

