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
This module helps in interacting with the filesystem.
The main focus is on abstracting files and directories and paths.

Path loads Files, Directories, etc.
Files have a path associated with them.
Directories are a collection of Paths (that link to other files and directories).

There is a circular dependency with these objects, so they need to be kept in one file.

"""
import os, re, random, subprocess, cPickle, shutil
import urllib
from datetime import datetime

from timestamp import Timestamp
from journal import Journal
from tag import Tags

def check_ignore(item, ignores=[]):
    """
    take a string (item)
    and see if any of the strings in ignores list are in the item
    if so ignore it.
    """
    ignore = False
    for i in ignores:
        if i and re.search(i, item):
            #print "ignoring item: %s for ignore: %s" % (item, i)
            ignore = True
    return ignore

def load_journal(path, **kwargs):
    """
    helper to simplify call
    """
    path = Path(path)
    return path.load_journal(**kwargs)

def load_instance(instances="/c/instances.txt", tag=None):
    """
    load instances.txt journal
    look for the newest entry with tag 
    return the data of the entry as a list of each file/line
    """
    j = load_journal(instances)
    if tag is not None:
        #if j.tag(tag):
        #    entries = j.tag(tag]
        #else:
        #    entries = []
        entries = j.tag(tag)
    else:
        entries = j
        
    if len(entries):
        #for sorting a list of entries:
        j2 = Journal()
        j2.update_many(entries)
        entries = j2.sort('reverse-chronological')

        #should be the newest entry with tag "tag"
        e = entries[0]
        items = e.data.splitlines()
        for i in items:
            #get rid of any empty strings from blank lines
            if not i:
                items.remove(i)
                
        #print items
        return items
    else:
        print "No instance entry found in journal: %s for tag: %s " % (instances, tag)
        return []
        
def name_only(name):
    """
    opposite of extension()
    return the filename without any extension
    """
    #make sure there is an extension
    ## new_name = ''
    ## #if name starts with a period, this will recurse infinitely:
    ## #if re.search('\.', name) and not re.match('\.', name):
    ## if re.search('\.', name):
    ##     parts = name.split('.')
    ##     only = parts[:-1]
    ##     temp = '.'.join(only)
    ##     new_name = temp
    ## else:
    ##     new_name = name
    ## #print new_name
    parts = os.path.splitext(name)
    new_name = parts[0]
    
    return new_name

def extension(name):
    """
    turns out that this is similar to os.path.splitext()
    but will only return the extension (not both parts)
    
    find a file's file extension (part of filename after last '.')

    splitting into a list with two items:
    prefix, extension = f.name.split(".")
    will not work with file names with multiple '.'s in them
    """
    #could also check if there is a '.' in the string, return none if not
    #parts = name.split('.')
    parts = os.path.splitext(name)
    extension = parts[-1]
    #print extension
    return extension


#from paths import *
#unless defined elsewhere, 
#will assume all paths passed in to Node objects are relative to this dir:
## relative_prefix = ''
## local_path = u'./'
## log_path = u'./'
## sort_config = 'alpha'

## config_log_in_outgoing = False
## config_log_in_media = False
## try:
##     #if not using in pylons, can define manually above
##     from pylons import config
##     if config.has_key('local_path'):
##         local_path = unicode(config['local_path'])
##     if config.has_key('log_local_path'):
##         log_path = unicode(config['log_local_path'])
##         config_log_in_outgoing = True
##     if config.has_key('log_in_media') and config['log_in_media'] == "True":
##         config_log_in_media = True
##     if config.has_key('sort_order'):
##         sort_config = config['sort_order']
##     if config.has_key('relative_prefix'):
##         relative_prefix = config['relative_prefix']
## except:
##     config = {}



class Path(object):
    """
    a path to a specific destination

    represented as a string with separators

    very similar in purpose to os.path

    is not involved with what is contained at the path destination

    this is a collection of common operations needed for manipulating paths,
    in some cases wrapping the standard library os.path module
    """
    
    def __init__(self, path=None, parts=None, relative=False, relative_prefix=''):
        """
        take either a relative or absolute path
        """

        #these get set in parse_path and parse_name
        self.name = ''
        self.extension = ''

        self.relative_prefix = relative_prefix
        
        self.parse_path(path, parts, relative, self.relative_prefix)

        #file (local), http, smb, etc
        self.protocol = ''

        self.separator = '/'
        

        #todo, general name for storage objects...
        #instances?  Node is *too* abstract... other things can be a node
        #but file is too specific
        #local instance? binary representation?
        
        #if a node has been loaded, can reference it here
        #or this could also be a property
        #that loads the node when called.
        self.storage = None

        #parent object
        self.content = None

        #self.filename = self._full_name
        
    def _get_filename(self):
        return self.name + self.extension
    def _set_filename(self, name):
        self.parse_name(name)
    filename = property(_get_filename, _set_filename)

    def _get_path(self):
        return os.path.join(self._dirname, self.filename)
    def _set_path(self, path):
        self.parse_path(path)
    path = property(_get_path, _set_path)
            
    def __str__(self):
        #this will fail if path has unicode characters it doesn't know 
        return str(self.path)
    
    def __unicode__(self):
        return unicode(self.path)

    def parse_name(self, name):
        #name without file extension:
        self.name = name_only(name)
        self.extension = extension(name)
        self._full_name = name

    def expand(self):
        """
        check if we start with a '.' something
        expand and reparse
        """
        if re.match('^\.', self.path):
            path = os.path.abspath(self.path)
            #print path
            self.parse_path(path)
        elif not (re.match('^/', self.path)):
            path = os.path.join('./', self.path)
            #print "Assuming relative, adding './' prefix: %s" % path
            path = os.path.abspath(self.path)
            self.parse_path(path)
        #otherwise must already be expanded... do nothing
        
    def parse_path(self, path=None, parts=None, relative=False, local_path=''):
        #print "parsing path: %s" % path
        #print "->%s<-" % path
        if not path and not parts:
            raise AttributeError, "Need either path or parts"

        if path:
            if path == ".":
                #special case... this will not get parsed correctly without
                #expanding it:
                path = os.path.abspath(path)
                #print path
                #path = os.path.abspath()
            #self._dirname = path
            #could check if it is an actual path here
            self._dirname = unicode(path)
        else:
            self._dirname = self.from_parts(parts)

        if relative:
            actual_path = os.path.join(unicode(local_path), self._dirname)
            actual_path = unicode(actual_path)
            actual_path = os.path.normpath(actual_path)
            self._dirname = actual_path

        #*2010.03.13 09:59:05
        #maybe it should be file_name or _file_name instead of full_name???
            
        #this should be a property, that combines name and extension
        #self.full_name = ''

        #http://docs.python.org/lib/module-os.path.html        
        self._full_name = os.path.basename(self._dirname)
        if not self._full_name:
            #might have been passed in a path with a trailing '/'
            self._dirname = os.path.dirname(self._dirname)
            self._full_name = os.path.basename(self._dirname)

        self._dirname = os.path.dirname(self._dirname)
        #print "fullname: %s" % self._full_name
        self.parse_name(self._full_name)
        
    def from_parts(self, parts):
        path = os.path.join(parts)
        return path
                   
    def type(self):
        """
        determine the subclass that should be associated with this Path
        this gives us a central place to track this
        """
        #PCD image format seems to cause a lot of trouble
        image_extensions = [ '.jpg', '.png', '.gif', '.jpeg', '.JPG', '.tif' ]
        movie_extensions = [ '.mpg', '.avi', '.flv', '.vob', '.wmv', '.AVI', '.iso', '.asf', '.mp4' ]

        #, 'm4p' are not playable by flash, should convert to use
        sound_extensions = [ '.mp3', '.wav', '.aif', '.ogg' ]

        journal_extensions = [ '.txt', '.log' ]

        #others
        #playlist_extensions = [ 'm3u', 'pls' ]
        #document_extensions = [ 'html', 'htm', 'mako' ]

        #determine what the right type of node should be based on path
        if (os.path.isfile(self.path)):
            #ext = extension(self.name)
            #print "Extension: %s" % self.extension
            ext = self.extension
            if ext in image_extensions:
                return "Image"
            elif ext in movie_extensions:
                return "Movie"
            elif ext in sound_extensions:
                return "Sound"
            elif ext in journal_extensions:
                return "Log"
            #elif ext in library_extensions:
            #    return "Library"
            #elif ext in playlist_extensions:
            #    return "Playlist"
            #elif ext in document_extensions:
            #    return "Document"
            else:
                return "File"

        elif (os.path.isdir(self.path)):
            return "Directory"
        else:
            print "Node... exists? %s Unknown filetype: %s" % (os.path.exists(self.path), self.path)
            raise ValueError
            #return "Node"

    def load(self, node_type=None, create=True):
        """
        return a storage.Node of the destination

        can look at types here
        and return the appropriate type

        looks at the path,
        determines the right kind of storage object to associate with that path
        returns the storage object
        """
        new_node = None
        if (create and not os.path.exists(self.path) and
            self.extension == ".txt"):
            #only want to create new log files, and then only if logging
            #is enabled
            #should be equivalent to a touch

            #f = file(self.path, 'w')
            #f.close()
            #print "creating"
            self.create()

        #to skip throwing an error if no file exists, uncomment following:
        #if os.path.exists(self.path):
        if not node_type:
            node_type = self.type()
            ## new_node = Node(self.path)
            ## node_type = new_node.find_type()
            ## if node_type in [ "Playlist", "Movie", "Document", "Library", "Log" ]:
            ##     #special case
            ##     node_type = "File"

        #ah ha!
        #passing in path as unicode is very important if planning to work
        #with unicode paths... otherwise gets converted to ascii here:
        #new_node = eval("%s(u'%s')" % (node_type, self.path))
        #above is causing trouble on windows, trying without

        #node_create = "%s(r'%s')" % (node_type, self.path)
        #node_create = r'%s("%s")' % (node_type, self.path)
        #re.subn(r"\\", r"\\\\", node_create)
        #new_node = eval(node_create)

        #2008.12.23 14:18:59
        #eval having a hard time with windows.  switching to a nested if-else:

        ## if node_type == "Node":
        ##     #new_node already defined:
        ##     pass
        if node_type == "Directory":
            new_node = Directory(self)
        elif node_type == "Image":
            new_node = Image(self)
        #elif node_type == "Sound":
        #    new_node = Sound(self.path)
        else: # node_type == "File":
            new_node = File(self)

        return new_node

    def load_journal(self, add_tags=[], subtract_tags=[],
                     include_path_tags=True, create=False):
        """
        walk the given path and
        create a journal object from all logs encountered in the path

        create a temporary, in memory, journal from logs

        this works for both directories and log files

        *2009.06.18 12:38:45

        this was started to be abstracted from osbrowser in player.py.  
        By moving here, we minimize dependencies outside of Moments module

        load_journal cannot guarantee that the returned Journal item will have a
        filename (self.path) associated with it for later saving.

        in that case should use:
        ::

          j = Journal()
          j.load(path, add_tags=these_tags)

        -or-
        ::

          j = load_journal(path)
          j.path = destination

        of course you can always pass the path in explicitly to save:
        save(filename=path)

        """
        #ignore_dirs = [ 'downloads', 'binaries' ]

        #this would be the place to add .hgignore items to the ignore_items list
        ignore_items = [ 'downloads', 'index.txt' ]
        j = Journal()
        log_check = re.compile('.*\.txt$')
        if os.path.isdir(self.path):
            for root,dirs,files in os.walk(self.path):
                for f in files:
                    #make sure it at least is a log file (.txt):
                    if not log_check.search(f):
                        continue

                    if not check_ignore(os.path.join(root, f), ignore_items):
                        these_tags = add_tags[:]
                        #will need to abstract context_tags() too... move to Tags
                        if include_path_tags:

                            #by default, we usually do not want to include
                            #the tags for self.path
                            #
                            #only subsequent path tags
                            #
                            #and only non-compact date tags

                            #find suffix:
                            cur_path = Path(os.path.join(root, f))

                            relative_path = cur_path.to_relative(str(self.path))
                            #print relative_path
                            relative_path = Path(os.path.join('/', relative_path))

                            filename_tags = relative_path.to_tags()

                            #journal.txt is often used as a default name
                            #in repositories
                            #but does not really indicate anything
                            #about the entries themselves (watered down)
                            #ok to remove if added by path
                            if "journal" in filename_tags:
                                filename_tags.remove("journal")
                                
                            for t in filename_tags:
                                try:
                                    ts = Timestamp(compact=t)
                                except:
                                    #if it's *not* a valid timestamp,
                                    #then we want to keep it as a tag
                                    if (str(t) != '01' and
                                        str(t) != '02' and
                                        str(t) != '03' and
                                        str(t) != '04' and
                                        str(t) != '05' and
                                        str(t) != '06' and
                                        str(t) != '07' and
                                        str(t) != '08' and
                                        str(t) != '09' and
                                        str(t) != '10' and
                                        str(t) != '11' and
                                        str(t) != '12'):
                                        these_tags.append(t)
                                    #print "adding: %s" % t
                            
                            

                        #subtract tags last:
                        for tag in subtract_tags:
                            if tag in these_tags:
                                these_tags.remove(tag)
                        j.load(os.path.join(root, f), add_tags=these_tags)

        elif os.path.isfile(self.path) and log_check.search(self.path):
            j.load(self.path, add_tags)
        elif create and log_check.search(self.path):
            #make a new log:
            j.save(self.path)
            j.load(self.path, add_tags)
        else:
            #no journal to create
            pass

        return j

    def exists(self):
        """
        check if the actual path exists.
        """
        return os.path.exists(self.path)

    def created(self):
        """
        wrapper shortcut for getting the modified timestamp of the path
        """
        if self.exists():
            f = self.load()
            return f.timestamp()
        else:
            return None

    def create(self, mode=None):
        """
        see if we have an extension
        create a blank file if so

        otherwise make a new directory
        """
        #print "Extension: %s" % self.extension
        if self.extension:
            f = file(self.path, 'w')
            f.close()
            assert self.exists()
        else:
            if mode:
                #os.mkdir(self.path, mode)
                os.makedirs(self.path, mode)
            else:
                #os.mkdir(self.path)
                os.makedirs(self.path)

    def remove(self):
        if os.path.exists(self.path):
            if self.type() == "Directory":
                shutil.rmtree(self.path)
            else:
                os.remove(self.path)
            
    def rename(self, destination):
        destination = str(destination)
        os.rename(str(self), destination)

    def move(self, destination):
        self.rename(destination)

    def copy(self, destination):
        """
        wrapping os call
        seems like there was trouble doing this if it crossed devices
        needed a system call in that case
        http://docs.python.org/library/shutil.html
        """
        shutil.copy(str(self), destination)
        
    #???
    def make_tree(self):
        """
        go through all parts and make a node for each of them
        return the root node
        """
        pass

    #def parent_path(self):
    def parent(self):
        """
        return a Path object to our parent
        don't want to do this on initialization,
        since it would recursively call
        
        Similar in concept to:
        os.path.dirname(self.path)
        """
        #make sure we have all the parts we can get:
        self.expand()
        
        if (self.path != os.path.dirname(self.path) and
            os.path.dirname(self.path)):
            
            parent_path = os.path.dirname(self.path)
            #print parent_path
            parent = Path(parent_path)
            return parent
        else:
            #special case for root path
            return None
            #return self #???
        
    #aka split_path
    #as_list
    def parts(self):
        """
        return a list of all parts of the path
        (os.path.split only splits into two parts, this does all)
        """
        #we'll be chopping this up
        path = self.path

        parts = []
        #make sure our path starts with a slash for a common end case
        if not re.match('^\/', path):
            path = os.path.join('/', path)
            #print "new: %s" % path
        while path and path != '/':
            (path, suffix) = os.path.split(path)
            parts.insert(0, suffix)

        #this will take care of windows paths that are being worked on in a unix environment manually
        new_parts = []
        for p in parts:
            new_parts.extend(p.split('\\'))

        parts = new_parts

        #print parts
        return parts

    #def path_to_tags(self):
    def to_tags(self, include_name=True, include_parent=True):
        """
        looks at the specified path to generate a list of tags
        based on the file name and location

        check if the last item in the path is a file with an extension
        get rid of the extension if so
        """

        all_tags = Tags()
        parts = []
        parent = self.parent()
        if parent and include_parent:
            path_parts = parent.parts()
            parts.extend(path_parts)
        if include_name:
            parts.append(self.name)

        #convert each item to tags individually
        #each item in a path could be made up of multiple tags
        #i.e work-todo
        for p in parts:
            if p:
                part_tags = Tags().from_tag_string(p)
                for tag in part_tags:
                    if tag not in all_tags:
                        all_tags.append(tag)

        return all_tags

    def distance(self, path):
        """
        the shortest number of nodes between self and path

        find common prefix
        then count from there
        """
        pass

    #def local_to_relative(path=None, add_prefix=False):
    #def to_relative(self, path='', leading_slash=False, extension=None):
    def to_relative(self, path='', extension=None):
        """
        should work either way...
        returns the difference between the two paths (self.path and path)
        return value is just a string representation
        
        accept a path (either Path or path... will get resolved down to str)
        return the relative part
        by removing the path sent from our prefix

        convert a local file path into one acceptable for use as a relative path in a URL

        if node is a file, this will include the filename at the end
        """
        if not path:
            path = self.relative_prefix
        #want to make sure that the path we're looking at contains local_path
        prefix = os.path.commonprefix([self.path, path])
        
        if prefix == self.path:
            #see if there is anything extra in the path part sent
            temp_path = path[len(prefix)+1:]
        else:
            temp_path = self.path[len(prefix):]
            
            ## if leading_slash:
            ##     temp_path = self.path[len(prefix):]
            ## else:
            ##     temp_path = self.path[len(prefix)+1:]
                
        #if re.search(r'\\', temp_path):
        #temp_path = re.subn(r'\\', '/', temp_path)
        temp_path = temp_path.replace(r'\\', '/')

        #if add_prefix:
        #    temp_path = os.path.join(config['relative_prefix'], temp_path)

        # this allows replacing an extension with something else
        # used in gallery scripts to replace .jpg with .html
        if extension:
            temp = Path(temp_path)
            temp.extension = extension
            temp_path = str(temp)
        
        return temp_path


    #should just use generalized local_to_relative if needed directly
    #*2009.03.15 22:28:06
    #in templates, is nice to have access to it through the object
    #wrapping general one
    #def relative_path(self, add_prefix=False):
    #    return local_to_relative(self.path, add_prefix)
    
    def custom_relative_path(self, prefix=None, path=None):
        """
        method to change system path to viewer path

        if path on file system is different than path displayed by viewer
        generate it here
        
        ideally would just use routes here... heavy overlap        
        """
        if not path:
            path = self.path

        if prefix:
            parts = (prefix, local_to_relative(path))
            try:
                #return urllib.quote(os.path.join(prefix, local_to_relative(path)))
                return urllib.quote('/'.join(parts))
            except:
                #return os.path.join(prefix, local_to_relative(path))
                return '/'.join(parts)
        else:
            #return urllib.quote(os.path.join('/', local_to_relative(path, add_prefix=True)))
            return urllib.quote(''.join(['/', local_to_relative(path, add_prefix=True)]))

    def relative_path_parts(self):
        """
        split the pieces up so that they can be navigated
        """
        parts = []
        path = self.to_relative()
        os.path.join('/', path)
        while path and path != '/':
            (prefix, suffix) = os.path.split(path)
            parts.insert(0, [suffix, path] )
            path = prefix
        return parts


    def log_action(self, actions=["view"]):
        """
        this is closely related to journal.log_action
        (don't forget to use that if it's easier)
        
        but sometimes it is inconvenient to think in terms of a journal
        when you are working with paths

        this assumes the journal to log into is "action.txt"
        if the path is a directory, look for it in the directory
        if the path is a file (more common)
        look for action.txt in the parent directory

        if logs need to be added anywhere else, use this concept, or journal.log_action
        """
        if self.type() == "Directory":
            d = self.load()
        else:
            d_path = self.parent()
            d = d_path.load()

        dest = os.path.join(str(d), "action.txt")
        j = load_journal(dest, create=True)
        #j = d.load_journal()
        entry = j.make(str(self.path), actions)
        j.save(dest)
        return entry
        

    
    #this is now parent().name:
    ## def parent_part(self):
    ##     """
    ##     could consider returning actual parent here
    ##     return the suffix and path for the parent directory only
    ##     """
    ##     parts = self.relative_path_parts()
    ##     return parts[-2]


#from path import Path, load_journal

#import os, re
#from storage import *
#from journal import Journal

#RENAME LocalNode ???
#StorageNode?
#DriveNode?

#class LocalNode(object):
#class File(LocalNode):
class File(object):
    """
    files are Nodes with sizes
    also leafs in tree structure

    could be a file or a directory

    one thing connected to other things on the filesystem
    
    structure to hold the meta data of a node on a filesystem
    should hold the common attributes of files and directories

    Node paths are the paths on the local system...
    i.e. how python would find them

    operations common to both files and directories
    """

    #def __init__(self, **kwargs):

    def __init__(self, path):
        #Node.__init__(self, **kwargs)
        #LocalNode.__init__(self, path)

        test = Path('.')
        if type(path) == type(test):
            self.path = path
        else:
            self.path = Path(path)

        #we don't initialize this since it could be a directory and
        #we don't want to recurse unless needed
        #can always call check_size later
        self.size = None

        self.check_stats()
        
        self.md5 = None
        #self.last_scan = None
        #self.last_scan = datetime.now()
        self.last_scan = Timestamp()

    def __str__(self):
        #this will fail if path has unicode characters it doesn't know 
        return str(self.path.filename)
    
    def __unicode__(self):
        return unicode(self.path.filename)

    def check_stats(self):
        """
        check and see what the operating system is reporting for
        this node's stats
        update our copy of the stats
        """
        #http://docs.python.org/lib/os-file-dir.html
        stat = os.stat(str(self.path))
        #st_atime (time of most recent access)
        self.atime = stat.st_atime
        #st_mtime (time of most recent content modification)
        self.mtime = stat.st_mtime
        #st_ctime (platform dependent; time of most recent metadata change on Unix, or the time of creation on Windows)
        self.ctime = stat.st_ctime        

    #*2010.12.21 09:23:04
    #TODO:
    #consider making size a property
    #Directory uses this too
    def check_size(self):
        """
        Wraps os.path.getsize() to return the file's size.
        """
        self.size = os.path.getsize(str(self.path))        
        return self.size
    
    def reset_stats(self):
        """
        some actions (like image rotate) may update the file's modified times
        but we might want to keep the original time
        this resets them to what they were when originally initialized
        """
        os.utime(str(self.path), (self.atime, self.mtime))

    def change_stats(self, accessed=None, modified=None):
        """
        take new values for the accessed and modified times and update the file's properties
        should only accept Timestamp values.
        Timestamp can be used for conversions as needed.
        then use Timestamp.epoch() to get right values here:
        """
        if accessed is None:
            new_atime = self.atime
        else:
            new_atime = accessed.epoch()

        if modified is None:
            new_mtime = self.mtime
        else:
            new_mtime = modified.epoch()
            
        os.utime(str(self.path), (new_atime, new_mtime))

        #keeps/restores the originals:
        #os.utime(self.path, (self.atime, self.mtime))

        self.check_stats()
        
    def adjust_time(self, hours=0):
        """
        wrap change stats in a more user friendly function
        """
        modified = Timestamp()
        modified.from_epoch(self.mtime)
        #print "Pre: %s" % modified

        #****configure your adjustment here****
        modified = modified.future(hours=hours)
        #**************************************

        accessed = Timestamp()
        accessed.from_epoch(self.atime)
        self.change_stats(accessed, modified)

        #reset to check:
        modified = Timestamp()
        modified.from_epoch(self.mtime)
        #print "Post: %s" % modified

    def move(self, rel_destination):
        """
        this utilizes the os.rename function
        """
        rel_parent = os.path.dirname(local_to_relative(self.path))
        destination = os.path.join(local_path, rel_parent, rel_destination)
        destination = os.path.normpath(destination)
        #new_dir = os.path.join(image_dir, data)
        (new_dir, new_name) = os.path.split(destination)

        #could also use os.renames()   note plural
        if not os.path.isdir(new_dir):
            os.mkdir(new_dir)
        os.rename(self.path, destination)

    def datetime(self):
        t = datetime.fromtimestamp(self.mtime)
        return t

    def day(self):
        """
        print creation time in a specific format
        """
        t = datetime.fromtimestamp(self.mtime)
        return t.strftime("%m/%d")

    def time(self):
        t = datetime.fromtimestamp(self.mtime)
        return t.strftime("%H:%M")

    def date(self):
        t = datetime.fromtimestamp(self.mtime)
        return t.strftime("%Y%m%d")

    def timestamp(self):
        """
        return a corresponding moments Timestamp object for the file's mtime
        """
        self.check_stats()
        modified = Timestamp()
        modified.from_epoch(self.mtime)
        return modified

    def make_md5(self):
        """
        calculate the md5 hash for ourself

        could store this in metadata at some point

        http://docs.python.org/library/hashlib.html#module-hashlib
        """
        import hashlib
        m = hashlib.md5()
        fd = open(str(self.path),"rb")
        m.update(fd.read())
        self.md5 = m.hexdigest()
        #not sure how this differs
        #self.md5 = m.digest()
        
        return self.md5
    

## #from sound import Sound
## class Sound(File):
##     """
##     object to hold sound/music specific meta data for local sound file

##     """
##     def __init__(self, path):
##         File.__init__(self, path)

#from image import Image
try:
    import Image as PILImage
except:
    try:
        #also check for Pillow version of PIL:
        import PIL.Image as PILImage
    except:
        print "WARNING: Python Image Library not intalled."
        print "Image manipulation will not work"

class Image(File):
    """
    object to hold Image specific meta data for an image locally available

    and rendering thumbnails
    """
    def __init__(self, path):
        File.__init__(self, path)
        self.thumb_dir_name = "sized"
        #2010.03.02 22:43:35 
        # could use the actual path object to handle this 
        #parent_dir_path = os.path.dirname(str(self.path))
        #self.thumb_dir_path = os.path.join(parent_dir_path, self.thumb_dir_name)
        self.thumb_dir_path = os.path.join(str(self.path.parent()),
                                           self.thumb_dir_name)
        
        #self.sizes = { 'tiny_o':'_t_o', 'tiny':'_t', 'small':'_s', 'medium':'_m', 'large':'_l' }
        self.sizes = { 'tiny':'_t', 'small':'_s', 'medium':'_m', 'large':'_l', 'xlarge':'_xl'}

        #parts = self.path.name.split('.')
        #self.last_four = parts[-2][-4:]
        self.last_four = self.path.name[-4:]

    def dimensions(self):
        """
        return the dimensions of this image
        """
        image = PILImage.open(str(self.path))
        return image.size

    ## def size_name(self, size):
    ##     """
    ##     take a size and create the corresponding thumbnail filename

    ##     *2012.08.18 11:24:30
    ##     deprecated...
    ##     seems like it's only used in self.size_path method
    ##     simple enough to just include it there
    ##     """
    ##     #parts = self.name.split('.')
    ##     #new_name = '.'.join(parts[:-1]) + self.sizes[size] + '.' + parts[-1]
    ##     #new_name = self.path.name + self.sizes[size] + '.' +self.path.extension
    ##     new_name = self.path.name + self.sizes[size] + self.path.extension
    ##     return new_name                  
        

    ## def get_size(self, size, relative=False):
    ##     """
    ##     when size_path() just isn't enough...
        
    ##     accepts: tiny, small, medium, large
    ##     """
    ##     thumb_path = self.size_path(size)
    ##     #if not os.path.isfile(thumb_path):
    ##     if not thumb_path.exists():
    ##         self.make_thumbs()

    ##     if relative:
    ##         #print self.path.relative_prefix
    ##         #thmb = Path(thumb_path, relative_prefix=self.path.relative_prefix)
    ##         thumb_path = thumb_path.to_relative()
    ##     return thumb_path

    def move(self, destination, relative=False):
        """
        this utilizes the os.rename function
        but should also move thumbnails

        if relative is true, will expect a relative path that is
        joined with the local path
        otherwise destination is assumed to be full local path

        very similar functionality as minstream.import_media._move_image_and_thumbs()
        import_media uses subprocess system level move commands
        which is not as cross platform
        """        
        #new_dir = os.path.join(image_dir, data)
        (new_dir, new_name) = os.path.split(destination)

        #could also use os.renames()   note plural
        if not os.path.isdir(new_dir):
            os.mkdir(new_dir)
        os.rename(self.path, destination)

        #move thumbnails
        new_image = Image(destination)
        #self.make_thumb_dirs(os.path.join(new_dir, self.thumb_dir_name))
        new_image.make_thumb_dirs()

        for k in self.sizes.keys():
            os.rename(self.size_path(k), new_image.size_path(k))

    def copy(self, destination, relative=True):
        """
        copy the original image, along with all thumbs
        """
        pass
            
    def size_path(self, size, square=True):
        """
        take a size and create the corresponding thumbnail (local) path

        *2012.08.18 11:28:13 
        also, decide if a squared version of the image is requested

        seems like this is something that should be done here
        (and maybe both should be available)

        """
        if size == 'tiny_o':
            #can keep the different tiny versions together:
            size_dir = 'tiny'
        else:
            size_dir = size

        if square:
            size_name = self.path.name + self.sizes[size] + '_sq' + self.path.extension
        else:
            size_name = self.path.name + self.sizes[size] + self.path.extension

        #thumb_path = os.path.join(self.thumb_dir_path, size_dir, self.size_name(size))
        thumb_path = os.path.join(self.thumb_dir_path, size_dir, size_name)
        return Path(thumb_path, relative_prefix=self.path.relative_prefix)

    def make_thumb_dirs(self, base=None):
        """
        if they don't already exist, create them
        """
        if not base:
            base = self.thumb_dir_path
        if not os.path.isdir(base):
            os.mkdir(base)
            
        #make separate directories for each thumbnail size
        for k in self.sizes.keys():
            if k != 'tiny_o':
                size_path = os.path.join(base, k)
                if not os.path.isdir(size_path):
                    os.mkdir(size_path)

    def _square_image(self, destination):
        if destination.size[0] != destination.size[1]:
            #lets make it a square:
            if destination.size[0] > destination.size[1]:
                bigger = destination.size[0]
                smaller= destination.size[1]
                diff = bigger - smaller
                first = diff/2
                last = bigger - (diff - first)
                box = (first, 0, last, smaller)
            else:
                bigger = destination.size[1]
                smaller= destination.size[0]
                diff = bigger - smaller
                first = diff/2
                last = bigger - (diff - first)
                box = (0, first, smaller, last)
            region = destination.crop(box)
            destination = region.copy()
        return destination
        
    def make_thumbs(self):
        """
        regenerate all thumbnails from original
        """
        ## if config.has_key('thumb.l'):
        ##     l = int(config['thumb.l'])
        ##     m = int(config['thumb.m'])
        ##     s = int(config['thumb.s'])
        ##     t = int(config['thumb.t'])
        ##     u = int(config['thumb.u'])
        ## else:

        #this is still big (maybe too big?)
        #but might shrink file size some?
        xl = 2880
        l = 1280
        m = 800
        s = 400
        t = 200
        #u = 25

        #*2012.08.18 12:23:19 
        #when rendering images for the web,
        #now it's a good idea to set dimensions to half the size
            
        name = self.path.name

        self.make_thumb_dirs()
        
        try:
            image = PILImage.open(str(self.path))
        except:
            print "Error opening image: %s" % str(self.path)
        else:
            #keep a copy of original for squaring
            square = image.copy()
            square = self._square_image(square)

            #made it this far... start resizing
            try:
                image.thumbnail((xl,xl), PILImage.ANTIALIAS)
            except:
                print "Error sizing image: %s" % str(self.path)
                exit()
            else:
                large = image.copy()
                large.thumbnail((l,l), PILImage.ANTIALIAS)

                medium = large.copy()
                medium.thumbnail((m,m), PILImage.ANTIALIAS)

                small = medium.copy()
                small.thumbnail((s,s), PILImage.ANTIALIAS)

                tiny = small.copy()
                tiny.thumbnail((t,t), PILImage.ANTIALIAS)

                #make squared versions
                #xl_sq = square.copy()
                #xl_sq.thumbnail((xl,xl), PILImage.ANTIALIAS)

                #l_sq = xl_sq.copy()
                l_sq = square.copy()
                l_sq.thumbnail((l,l), PILImage.ANTIALIAS)

                m_sq = l_sq.copy()
                m_sq.thumbnail((m,m), PILImage.ANTIALIAS)

                s_sq = m_sq.copy()
                s_sq.thumbnail((s,s), PILImage.ANTIALIAS)

                t_sq = s_sq.copy()
                t_sq.thumbnail((t,t), PILImage.ANTIALIAS)

                #o for original dimensions
                #tiny_o = image.copy()
                #we want to fix the width at t, not concerned about height
                #tiny_o.thumbnail((t,1000), PILImage.ANTIALIAS)

                ## try:
                image.save(str(self.size_path('xlarge', square=False)), "JPEG")
                large.save(str(self.size_path('large', square=False)), "JPEG")
                medium.save(str(self.size_path('medium', square=False)), "JPEG")
                small.save(str(self.size_path('small', square=False)), "JPEG")
                tiny.save(str(self.size_path('tiny', square=False)), "JPEG")

                l_sq.save(str(self.size_path('large')), "JPEG")
                m_sq.save(str(self.size_path('medium')), "JPEG")
                s_sq.save(str(self.size_path('small')), "JPEG")
                t_sq.save(str(self.size_path('tiny')), "JPEG")

                
                #tiny_o.save(str(self.size_path('tiny_o')), "JPEG")
                ## except:
                ##     print "error generating thumbs for: %s" % self.path.name
                ##     #pass

    ## def reset_stats(self):
    ##     """
    ##     some actions (like image rotate) may update the file's modified times
    ##     but we might want to keep the original time

    ##     this should redefine File.reset_stats for images only
    ##     """
    ##     #this resets them to what they were when originally initialized
    ##     #os.utime(str(self.path), (self.atime, self.mtime))

    ##     #might be better to get the actual time from the image meta data
    ##     os.system("jhead -ft %s" % (self.path))

    def datetime_exif(self):
        #resets the timestamp of the file to what was stored in exif header
        #this will print the filepath to the console
        meta = os.system("jhead -ft %s" % (self.path))
        #print "TIMESTAMP FROM EXIF: %s" % meta
        #not sure that meta will have a value here
        #just 0, no error
        #return meta

    def rotate_pil(self, degrees=90):
        """
        rotate image by number of degrees (clockwise!!)

        use Python Image Library

        PIL is very LOSSY!!

        will also lose original EXIF data

        (but it does work if you don't have access to jhead/jpegtran)
        """
        #standard PIL goes counter-clockwise
        #should adjust here
        degrees = 360 - float(degrees)
        image = PILImage.open(self.path)
        im2 = image.rotate(float(degrees))
        im2.save(self.path, "JPEG")
        self.make_thumbs()
        self.reset_stats()
        
    def rotate(self, degrees=90):
        """
        rotate image by number of degrees (clockwise!!)

        need to reset file timestamp to be original
        especially if not keeping track of that elsewhere

        see also Directory.auto_rotate_images()

        but if you need to tune individually, better to call jpegtrans here

        jhead -cmd "jpegtran -progressive -rotate 90 &i > &o" IMG_4965.JPG

        http://www.sentex.net/~mwandel/jhead/usage.html
        """
        os.system("jhead -cmd \"jpegtran -progressive -rotate %s &i > &o\" %s" % (degrees, self.path))
        self.make_thumbs()
        self.reset_stats()

    def auto_rotate(self):
        result = ''
        jhead = subprocess.Popen("jhead -autorot %s" % self.path, shell=True, stdout=subprocess.PIPE)
        current = jhead.communicate()[0]
        #print "Finished rotating: %s, %s" % (self.name, current)
        if current: print current
        result += current
        #make sure timestamps stay the same
        self.reset_stats()
        return result

class Directory(File):
    """
    This object holds a summary of a single directory.
    (no recursion.  one level only)

    A Directory is a collection of Path objects. 
    They can be sortable based on types, dates, etc.
    Each of the Paths can handle loading and types.

    Directories on the filesystem share many properties with Files,
    so the Directory class is a subclass of the File class. 
    """
    def __init__(self, path='', **kwargs):
        File.__init__(self, path, **kwargs)

        #print "initializing directory: %s" % self.path


        #self.ignores = []
        self.ignores = [ '.hg', '.hgignore', '.svn', 'index.xml', 'meta.txt', 'sized', '.DS_Store', '.HFS+ Private Directory Data', '.HFS+ Private Directory Data\r', '.fseventsd', '.Spotlight-V100', '.TemporaryItems', '.Trash-ubuntu', '.Trashes', 'lost+found' ]

        self.reset()
        
        self.scan_directory()

    def reset(self):
        """
        if we've already scanned something once, and a subsequent scan is called,
        we'll want to reset ourself so duplicates are not added (common mistake)
        this is the same thing that happens during initialization,
        so breaking it out here
        """
        #string only version
        #(sometimes it is easier to use just strings... like diff directories)
        self.listdir = []

        #everything
        self.contents = []

        self.files = []
        self.directories = []

        self.playlists = []
        self.libraries = []
        self.images = []
        self.sounds = []
        self.movies = []
        self.logs = []
        self.documents = []
        self.other = []

        self.last_scan = None
        self.filetypes_scanned = False

        #how many items we have total
        self.count = 0

        
    def scan_directory(self, recurse=False):
        """
        only load paths

        this will clear out any previous scans to avoid duplication
        reset includes filetypes and sorts
        """
        if self.last_scan:
            self.reset()
            
        self.listdir = os.listdir(unicode(self.path))
        for item in self.listdir:
            if item not in self.ignores:
                self.count += 1
                
                #print "SUPPORTS UNICODE: %s" % os.path.supports_unicode_filenames
                if os.path.supports_unicode_filenames:
                    item_path = os.path.normpath(os.path.join(unicode(self.path), item))
                else:
                    #item_path = unicode(self.path) + u'/' + unicode(item)
                    try:
                        item_path = os.path.normpath(os.path.join(str(self.path), item))
                    except:
                        item_path = ''
                        print "could not open: %s" % item

                item_path = unicode(item_path)
                #propagate any relative settings passed to us
                node = Path(item_path, relative_prefix=self.path.relative_prefix)

                #everything
                self.contents.append(node)
                
                if (os.path.isfile(item_path)):
                    self.files.append(node)
                    
                elif (os.path.isdir(item_path)):
                    self.directories.append(node)

                else:
                    print "ERROR: unknown item found; not a file or directory:"
                    print item_path

        self.last_scan = Timestamp()

        #if we don't sort now, it will be more work to sort later
        #self.directories.sort()
        
    def scan_filetypes(self):
        """
        look in the directory's list of files for different types of files
        put them in the right list type in the directory

        should have already scanned the directory for files

        we will look through the list of files
        for files that are likely images
        then populate that list

        not sure if this should always happen at scan time
        what if we don't need to use images, sounds, movies?  extra step
        maybe only create special node types if they're needed. 
        
        depending on the file extension, should create an object
        with the appropriate type
        and add it to the correct list in the Directory
        
        """        
        # we should only need to scan the filetypes once per instance:
        # (don't want to end up with duplicates)
        if not self.filetypes_scanned:
            for f in self.files:
                t = f.type()
                if (t == "Image"):
                    self.images.append(f)
                elif (t == "Movie"):
                    self.movies.append(f)
                elif (t == "Playlist"):
                    self.playlists.append(f)
                elif (t == "Sound"):
                    self.sounds.append(f)
                elif (t == "Log"):
                    self.logs.append(f)
                elif (t == "Document"):
                    self.documents.append(f)
                else:
                    #must be something else:
                    self.other.append(f)

            self.filetypes_scanned = True
                    
    def sort_by_date(self):
        dates = []

        #just in case something is looking
        #at 1 of the 3 main groups for a directory
        #(contents, files, directories)
        #instead of just files (more common)
        #we'll update all 3

        for f in self.contents:
            date = f.load().datetime()
            dates.append( (date, f) )
        dates.sort()
        self.contents = []
        self.files = []
        self.directories = []
        
        #print "AFTER SORT: "
        for d in dates:
            #print "%s, %s" % (d[0], d[1])
            item_path = d[1]
            self.contents.append(item_path)

            if (os.path.isfile(str(item_path))):
                self.files.append(item_path)

            elif (os.path.isdir(str(item_path))):
                self.directories.append(item_path)


    def sort_by_path(self, filetype=None):
        if filetype is not None:
            if (filetype == "File"):
                self.files = self.sort_helper(self.files)
            elif (filetype == "Directory"):
                self.directories = self.sort_helper(self.directories)
            elif (filetype == "Image"):
                self.images = self.sort_helper(self.images)
            elif (filetype == "Movie"):
                self.movies = self.sort_helper(self.movies)
            elif (filetype == "Playlist"):
                self.playlists = self.sort_helper(self.playlists)
            elif (filetype == "Sound"):
                self.sounds = self.sort_helper(self.sounds)
            elif (filetype == "Log"):
                self.logs = self.sort_helper(self.logs)
            elif (filetype == "Document"):
                self.documents = self.sort_helper(self.documents)

        else:
            #recursively call self for all filetypes
            all_types = [ "Image", "Movie", "Playlist", "Sound", "Log",
                          "Document", "File", "Directory" ]
            for t in all_types:
                self.sort_by_path(filetype=t)
            self.contents = self.sort_helper(self.contents)

    def sort_helper(self, collection):
        strings = []
        for item in collection:
            strings.append(unicode(item))
        strings.sort()
        paths = []
        for s in strings:
            paths.append(Path(s, relative_prefix=self.path.relative_prefix))
        return paths                

    def check_size(self, recurse=False):
        """
        Go through all files and add up the size. 

        It is possible to recursively add up sizes of subdirectories,
        but this can be a resource intensive operation.
        Be careful when setting recurse=True. 
        """
        if not self.size:
            for item_path in self.files:
                node = File(item_path)
                node.check_size()
                if not self.size:
                    self.size = node.size
                else:
                    self.size += node.size
                    
            if recurse:
                for d in self.directories:
                    sub_d = d.load()
                    self.size += sub_d.directory_size(recurse)
            else:
                #print "Not recursing; no size found for sub-directories"
                #print item_path
                pass

    def file_date_range(self):
        """
        generate a name based on the range of dates for files in this directory
        """
        self.sort_by_date()

        new_name = ''
        start = self.files[0].date()
        end = self.files[-1].date()
        if start != end:
            new_name = start + '-' + end
        else:
            new_name = start

        return new_name

    def adjust_time(self, hours=0):
        """
        adjust the modified time of all files in the directory by the number
        of hours specified.
        """
        for fpath in self.files:
            f = fpath.load()
            f.adjust_time(hours)
        
    def files_to_journal(self, filetype="Image", journal_file="action.txt", full_path=False):
        """
        *2010.12.22 06:49:41
        seems similar in function to create_journal
        this is a bit easier to understand from the name though

        this is used by
        /c/moments/scripts/import_usb.py

        """
        #just incase we haven't:
        self.scan_filetypes()
        
        jpath = os.path.join(str(self.path), journal_file)
        j = load_journal(jpath, create=True)

        files = []
        tags = []
        if filetype == "Image":
            files = self.images
            tags = [ 'camera', 'image', 'capture', 'created' ]
        elif filetype == "Sound":
            files = self.sounds
            tags = [ 'sound', 'recorded', 'created' ]
        elif filetype == "File":
            files = self.files
            tags = [ 'file', 'created' ]

        for fpath in files:
            #could also use j.make() here:
            #e = Moment()
            #e.created = Timestamp(i.datetime())
            #e.tags = tags
            #e.data = i.path
            #j.update_entry(e)
            f = fpath.load()
            if full_path:
                data = str(fpath)
            else:
                data = str(fpath.filename)
            j.make(data=data, tags=tags, created=f.datetime())

        #print j
        #j.sort_entries("reverse-chronological")
        #l = Log(filename)
        #j.save('temp.txt')
        j.save(jpath, order="reverse-chronological")

    def create_journal(self, journal="action.txt", items="Images", full_path=False):
        """
        if we don't have a journal
        create one using the items of type items

        adapted from moments/scripts/images_to_journal.py
        """
        j = None
        source = os.path.join(str(self.path), journal)
        if os.path.exists(source):
            j = Journal()
            j.load(source)

        source = os.path.join(str(self.path), journal)
        if not j:
            self.scan_filetypes()

            #this will not propigate to log
            #creation times will take priority
            #self.sort_by_path("Image")
            
            #print self.images
            #app.sources = self.images
            j = Journal()

            #TODO:
            #if other item types are desired in the log
            #items can be a list of types to check for
            
            for i in self.images:
                image = i.load()
                #e = Moment()

                #this works, but if the file timestamp has been modified
                #it won't be set to when the picture was taken:
                created = Timestamp(image.datetime())

                tags = [ 'image' ]
                #*2010.12.28 16:51:12 
                #image.path is likely to change over time
                #as tags are added to the directory, etc
                #just use the file name in the local action tags
                #elsewhere, full path is fine, knowing that it might change, but better than nothing
                if full_path:
                    data = str(i)
                else:
                    data = str(i.filename)
                #j.update_entry(e)
                j.make(data, tags, created)

            j.save(source, order="chronological")

        else:
            print "Journal: %s already exists" % (source)

        return j

    #rename to generate_thumbnails?        
    def make_thumbs(self):
        """
        generate thumbnails for all images in this directory
        """
        self.scan_filetypes()
            
        if len(self.images):
            for i in self.images:
                i.load().make_thumbs()

    def default_file(self):
        """
        usually just want an image
        but if there are no images, we may want to look for other file types
        """
        pass

    def summary(self):
        """
        standard way of representing the directory concisely?
        """
        pass

    def default_image(self, pick_by="random"):
        """
        if we have an action log, use that regardless of pick_by

        Not currently configured to work with RemoteJournal
        """
        self.scan_filetypes()
        #print "%s has %s images" % (self.path.name, len(self.images))
        choice = None           
        if len(self.images):

            dest = os.path.join(str(self.path), "action.txt")
            j = load_journal(dest)
            if j:
                #2009.12.19 13:19:27 
                #need to generate the data association first now
                j.associate_files()

                most_frequent = j._files.frequency_list()
                most_frequent.sort()
                most_frequent.reverse()
                if self.path.name == "20100522-rebel-slr":
                    print most_frequent
                while not choice and len(most_frequent):
                    next_option = most_frequent.pop(0)
                    file_part = next_option[1].strip()
                    path_part = os.path.join(str(self.path), file_part)
                    path = Path(path_part, relative_prefix=self.path.relative_prefix)
                    if path.exists():
                        if path.type() == "Image":
                            choice = path

                    else:
                        print "couldn't find: %s" % path
                
            elif pick_by == "random":
                random.seed()
                r = random.randint(0, len(self.images)-1)
                choice = self.images[r]

            else:
                choice = self.images[0]
                #must not have found anything statistical if we make it here
                #just return the first one in the list

        else:
            #print "No images available in: %s" % self.path.name
            #choice will be None:
            pass

        #FOR DEBUG:
        ## if choice:
        ##     print "default image: %s" % choice.path
        ## else:
        ##     print "NO IMAGE FOUND!"

        return choice

    def auto_rotate_images(self, update_thumbs=True):
        """
        #it's best to just use:
        jhead -autorot *.JPG

        this resets the last modified timestamp to now()
        not what we want, so go through and reset all timestamps
        to original times

        http://www.sentex.net/~mwandel/jhead/
        """
        self.scan_filetypes()
        #image_list = self.get_images()
        #images = image_list.as_objects()
        #images = self.images

        #load the images as File based objects so that we can reset timestamps later
        #print "loading images:"
        images = []
        for ipath in self.images:
            i = ipath.load()
            images.append(i)

        #os.system("jhead -autorot %s/*.JPG" % self.path)
        #result = os.popen("jhead -autorot %s/*.JPG" % self.path)
        #jhead = subprocess.Popen("jhead -autorot %s/*.JPG" % self.path, shell=True, stdout=subprocess.PIPE)
        #jhead.wait()
        #result = jhead.stdout.read()

        #print "rotating images:"
        result = ''
        for i in images:
            result += i.auto_rotate()
            
        #similar issue with thumbnails... not updated
        #for these we only want to regenerate those that changed for speed
        #print "regenerating thumbnails:"
        new_result = ''
        if update_thumbs:
            for line in result.split('\n'):
                if line:
                    (x, path) = line.split('Modified: ')
                    new_result += path + '\n'
                    i = Image(path)
                    i.make_thumbs()
                
        #can reset all image stat, even those not rotated, just to simplify task
        #print "resetting file timestamps:"
        for i in images:
            i.reset_stats()

        return new_result


