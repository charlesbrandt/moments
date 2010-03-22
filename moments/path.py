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
*2009.10.21 16:07:53 
module for interacting with the filesystem.
Main focus is on abstracting files and directories and paths.

adapted from osbrowser package.

Path loads Files, Directories, etc
Files, Directories, etc have a path associated with them
circular dependency
hence, one file
"""
import os, re, random, subprocess
import urllib
from datetime import datetime

from timestamp import Timestamp
from journal import Journal
from association import check_ignore

from tags import Tags

def load_journal(path, **kwargs):
    """
    helper to simplify call
    """
    path = Path(path)
    return path.load_journal(**kwargs)

def name_only(name):
    """
    opposite of extension()
    return the filename without any extension
    """
    #make sure there is an extension
    new_name = ''
    if re.search('\.', name):
        parts = name.split('.')
        only = parts[:-1]
        temp = '.'.join(only)
        new_name = temp
    else:
        new_name = name
    #print new_name
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
relative_prefix = ''
local_path = u'./'
log_path = u'./'
sort_config = 'alpha'

config_log_in_outgoing = False
config_log_in_media = False
try:
    #if not using in pylons, can define manually above
    from pylons import config
    if config.has_key('local_path'):
        local_path = unicode(config['local_path'])
    if config.has_key('log_local_path'):
        log_path = unicode(config['log_local_path'])
        config_log_in_outgoing = True
    if config.has_key('log_in_media') and config['log_in_media'] == "True":
        config_log_in_media = True
    if config.has_key('sort_order'):
        sort_config = config['sort_order']
    if config.has_key('relative_prefix'):
        relative_prefix = config['relative_prefix']
except:
    config = {}


class Path(object):
    """
    a path to a specific destination

    represented as a string with separators

    very similar in purpose to os.path

    is not involved with what is contained at the path destination

    this is a collection of common operations needed for manipulating paths,
    in some cases wrapping the standard library os.path module
    """
    
    def __init__(self, path=None, parts=None, relative=False, local_path=''):
        """
        take either a relative or absolute path
        """

        #these get set in parse_path and parse_name
        self.name = ''
        self.extension = ''
        
        self.parse_path(path, parts, relative, local_path)

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

    def parse_path(self, path=None, parts=None, relative=False, local_path=''):
        #print "parsing path: %s" % path
        if not path and not parts:
            raise AttributeError, "Need either path or parts"

        if path:
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
        movie_extensions = [ '.mpg', '.avi', '.flv', '.vob', '.wmv', '.AVI', '.iso', '.asf' ]

        #, 'm4p' are not playable by flash, should convert to use
        sound_extensions = [ '.mp3', '.wav', '.aif', '.ogg' ]

        journal_extensions = [ '.txt', '.log' ]

        #others
        #playlist_extensions = [ 'm3u', 'pls' ]
        #document_extensions = [ 'html', 'htm', 'mako' ]

        #determine what the right type of node should be based on path
        if (os.path.isfile(self.path)):
            #ext = extension(self.name)
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
            return "Node"

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
            new_node = Directory(self.path)
        elif node_type == "Image":
            new_node = Image(self.path)
        #elif node_type == "Sound":
        #    new_node = Sound(self.path)
        else: # node_type == "File":
            new_node = File(self.path)

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
          j.from_file(path, add_tags=these_tags)

        -or-
        ::

          j = load_journal(path)
          j.path = destination

        of course you can always pass the path in explicitly to to_file:
        to_file(filename=path)

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
                            filename_tags = Path(os.path.join(root, f)).to_tags()
                            these_tags.extend(filename_tags)
                        #subtract tags last:
                        for tag in subtract_tags:
                            if tag in these_tags:
                                these_tags.remove(tag)
                        j.from_file(os.path.join(root, f), add_tags=these_tags)

        elif os.path.isfile(self.path) and log_check.search(self.path):
            j.from_file(self.path, add_tags)
        elif create and log_check.search(self.path):
            #make a new log:
            j.to_file(self.path)
            j.from_file(self.path, add_tags)
        else:
            #no journal to create
            pass
        return j

    def exists(self):
        """
        check if the actual path exists.
        """
        return os.path.exists(self.path)

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
            os.remove(self.path)
            
    def rename(self, destination):
        destination = str(destination)
        os.rename(str(self), destination)

    def move(self, destination):
        self.rename(destination)

        
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
        
    ## def parent(self):
    ##     """
    ##     return a Directory object for the current Node's parent 
    ##     """
    ##     if self.path != os.path.dirname(self.path):
    ##         parent_path = os.path.dirname(self.path)
    ##         parent = Directory(parent_path)
    ##         return parent
    ##     else:
    ##         #special case for root directory
    ##         return self

    ## def get_parent(self):
    ##     pass

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
        #print parts
        return parts

    #def path_to_tags(self):
    def to_tags(self, include_name=True):
        """
        looks at the specified path to generate a list of tags
        based on the file name and location

        check if the last item in the path is a file with an extension
        get rid of the extension if so
        """

        all_tags = Tags()
        parts = []
        parent = self.parent()
        if parent:
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

    ## def context_tags(self):
    ##     """
    ##     looks at the relative path and filename to generate a list of tags
    ##     based on the file name and location

    ##     *2009.06.18 13:11:55 
    ##     could consider using moments.tags.path_to_tags
    ##     but this likely approaches the problem slightly differently
    ##     """
    ##     all_tags = []
    ##     rel_parent_dir = os.path.dirname(local_to_relative(self.path))
    ##     path_parts = split_path(rel_parent_dir)
    ##     #since each item in a path could be made up of multiple tags
    ##     #i.e work-todo
    ##     for p in path_parts:
    ##         if p:
    ##             ptags = Tags().from_tag_string(p)
    ##             #ptags = tags_from_string(p)
    ##             for pt in ptags:
    ##                 if pt not in all_tags:
    ##                     all_tags.append(pt)
    ##     #name_tags = tags_from_string(self.name_only)
    ##     name_tags = Tags().from_tag_string(self.name_only)

    ##     #print "name tags: %s, name_only: %s" % (name_tags, self.name_only)
    ##     for nt in name_tags:
    ##         if nt not in all_tags:
    ##             all_tags.append(nt)
    ##     #all_tags.extend(name_tags)
    ##     #print "all tags: %s" % all_tags
    ##     return all_tags

    def distance(self, path):
        """
        the shortest number of nodes between self and path

        find common prefix
        then count from there
        """
        pass

    #def local_to_relative(path=None, add_prefix=False):
    def to_relative(self, path):
        """
        accept a path (either Path or path... will get resolved down to str)
        return the relative part
        by removing the path sent from our prefix

        return a new path object

        convert a local file path into one acceptable for use as a relative path in a URL

        if node is a file, this will include the filename at the end!!!
        """
        #want to make sure that the path we're looking at contains local_path
        prefix = os.path.commonprefix([local_path, path])
        if prefix == local_path:
            #take everything after prefix as relative
            temp_path = path[len(prefix)+1:]
        else:
            #not sure what was sent, might as well just give it back
            temp_path = path

        #if re.search(r'\\', temp_path):
        #temp_path = re.subn(r'\\', '/', temp_path)
        temp_path = temp_path.replace(r'\\', '/')

        if add_prefix:
            temp_path = os.path.join(config['relative_prefix'], temp_path)
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

    def relative_path_parts(self, path=''):
        """
        split the pieces up so that they can be navigated
        """
        parts = []
        if not path:
            path = self.path
        path = local_to_relative(path)
        os.path.join('/', path)
        while path and path != '/':
            (prefix, suffix) = os.path.split(path)
            parts.insert(0, [suffix, path] )
            path = prefix
        return parts


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
        return str(self.path)
    
    def __unicode__(self):
        return unicode(self.path)

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

    def check_size(self):
        self.size = os.path.getsize(str(self.path))        
        return self.size
    
    def reset_stats(self):
        """
        some actions (like image rotate) may update the file's modified times
        but we might want to keep the original time
        this resets them to what they were when originally initialized
        """
        os.utime(self.path, (self.atime, self.mtime))

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


##     #should be load_journal  ... not really creating a new file here
       # and if you need load_journal, just import the load journal
       # directly from the journal object instead. (pass it the node path)
##     def create_journal(self, add_tags=[]):
##         """
##         create a temporary, in memory journal from logs
        
##         this works for both directories and log files

##         *2009.10.21 16:19:05
##         should just call journal.load_journal
##         """
##         print "DEPRECATED: node.create_journal, please call load_journal"
##         return load_journal(self.path)

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
    

# should just call journal.log_action directly
##     def log_action(self, actions=["access"], data=None,
##                    log_in_media=False, log_in_outgoing=False, outgoing=None):

## #from sound import Sound
## class Sound(File):
##     """
##     object to hold sound/music specific meta data for local sound file

##     """
##     def __init__(self, path):
##         File.__init__(self, path)

#from image import Image
import Image as PILImage

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
        
        self.sizes = { 'tiny_o':'_t_o', 'tiny':'_t', 'small':'_s', 'medium':'_m', 'large':'_l' }

        #parts = self.path.name.split('.')
        #self.last_four = parts[-2][-4:]
        self.last_four = self.path.name[-4:]

    def size_name(self, size):
        """
        take a size and create the corresponding thumbnail filename
        """
        #parts = self.name.split('.')
        #new_name = '.'.join(parts[:-1]) + self.sizes[size] + '.' + parts[-1]
        #new_name = self.path.name + self.sizes[size] + '.' +self.path.extension
        new_name = self.path.name + self.sizes[size] + self.path.extension
        return new_name                  
        
    def size_path(self, size):
        """
        take a size and create the corresponding thumbnail (local) path 
        """
        if size == 'tiny_o':
            #can keep the different tiny versions together:
            size_dir = 'tiny'
        else:
            size_dir = size
        thumb_path = os.path.join(self.thumb_dir_path, size_dir, self.size_name(size))
        return thumb_path

    ## def size_path_relative(self, size):
    ##     """
    ##     some overlap here with relative_path,
    ##     but it isn't working for thumbnails anyway
    ##     """            
    ##     if size == 'full':
    ##         return os.path.join(relative_prefix, local_to_relative(self.path))
    ##     else:
    ##         return os.path.join(relative_prefix, os.path.dirname(local_to_relative(self.path)), self.thumb_dir_name, size, self.size_name(size))
        

    def get_size(self, size):
        """
        tiny, small, medium, large
        """
        thumb_path = self.size_path(size)
        if not os.path.isfile(thumb_path):
            self.make_thumbs()
        return thumb_path

    def move(self, destination, relative=True):
        """
        this utilizes the os.rename function
        but should also move thumbnails

        if relative is true, will expect a relative path that is
        joined with the local path
        otherwise destination is assumed to be full local path
        """
        if relative:
            destination = os.path.join(local_path, destination)
        
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

    def _square_image(self, small):
        if small.size[0] != small.size[1]:
            #lets make it a square:
            if small.size[0] > small.size[1]:
                bigger = small.size[0]
                smaller= small.size[1]
                diff = bigger - smaller
                first = diff/2
                last = bigger - (diff - first)
                box = (first, 0, last, smaller)
            else:
                bigger = small.size[1]
                smaller= small.size[0]
                diff = bigger - smaller
                first = diff/2
                last = bigger - (diff - first)
                box = (0, first, smaller, last)
            region = small.crop(box)
            small = region.copy()
        return small
        
    def make_thumbs(self):
        """
        regenerate all thumbnails from original
        """
        if config.has_key('thumb.l'):
            l = int(config['thumb.l'])
            m = int(config['thumb.m'])
            s = int(config['thumb.s'])
            t = int(config['thumb.t'])
            u = int(config['thumb.u'])
        else:
            l = 1280
            m = 800
            s = 200
            t = 100
            u = 25
            
        name = self.path.name

        self.make_thumb_dirs()
        
        #remove exisiting thumbs before regen?
        #or does save overwrite anyway?
        #for s in self.sizes.keys():
        #    if os.path.isdir(self.size_path(s)):
        #        os.remove(self.size_path(s))

        #try:
        image = PILImage.open(str(self.path))
        image.thumbnail((l,l), PILImage.ANTIALIAS)

        medium = image.copy()
        medium.thumbnail((m,m), PILImage.ANTIALIAS)
        
        small = medium.copy()
        small = self._square_image(small)
        small.thumbnail((s,s), PILImage.ANTIALIAS)

        tiny = small.copy()
        tiny.thumbnail((t,t), PILImage.ANTIALIAS)

        #o for original dimensions
        tiny_o = image.copy()
        #we want to fix the width at t, not concerned about height
        tiny_o.thumbnail((t,1000), PILImage.ANTIALIAS)

        try:
            image.save(self.size_path('large'), "JPEG")
            medium.save(self.size_path('medium'), "JPEG")
            small.save(self.size_path('small'), "JPEG")
            tiny.save(self.size_path('tiny'), "JPEG")
            tiny_o.save(self.size_path('tiny_o'), "JPEG")
        except:
            print "error generating thumbs for: %s" % self.path.name
            #pass

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
        """
        os.system("jhead -cmd \"jpegtran -progressive -rotate %s &i > &o\" %s" % (degrees, self.path))
        self.make_thumbs()
        self.reset_stats()

class Directory(File):
    """
    
    object to hold a summary of a single directory
    (no recursion.  one level only)

    The important thing here is that we represent a Directory and the meta data
    most code would need for working with a directory (without needing the
    directory itself)

    """
    def __init__(self, path='', recurse=False, meta_enabled=True, **args):
        """
        check if there is already an index in the path
        if so load it
        otherwise create one.
        """
        File.__init__(self, path, **args)

        #print "initializing directory: %s" % self.path

        #*2010.03.01 19:15:33 TODO rename: count?
        self.items = 0

        #names only!!
        #everything
        self.contents = []

        #this will be a list of paths to prevent recursion
        self.sub_paths = []
        
        #self.ignores = []
        self.ignores = [ '.hg', '.svn', 'index.xml', 'index.txt', 'meta.txt', 'sized', '.DS_Store', '.HFS+ Private Directory Data', '.HFS+ Private Directory Data\r', '.fseventsd', '.Spotlight-V100', '.TemporaryItems', '.Trash-ubuntu', '.Trashes', 'lost+found' ]

        #these should be osbrowser.File python objects
        self.files = []

        self.filetypes_scanned = False
        #*2009.06.10 07:22:54 
        #safe to just call these directories?
        #*2009.10.21 16:14:24
        # renamed from self.sub_directories to self.directories
        # (haven't refactored any code that may use it)
        self.directories = []
        self.playlists = []
        self.libraries = []
        self.images = []
        self.sounds = []
        self.movies = []
        self.logs = []
        self.documents = []
        self.other = []

        #depending on context, might want to know the default page
        #or might want to know the default image
        #self.default_image = ""
        self.default_node = ""

        if not self.find_and_load_index():
            self.scan_directory(recurse)

    def find_and_load_index(self):
        """
        should scan path for different versions of existing indexes
        (if one exists)

        *2009.12.15 09:44:59
        right now this just creates an index every time
        """
        found = False

        #try to load:
        #index = "index.xml"
        options = []
        for o in options:
            filename = os.path.join(self.path, o)
            self.filename = filename

            if os.path.isfile(filename):
                found = True
                self.tree = ElementTree.ElementTree(file=filename)
                self.root = self.tree.getroot()

        return found

    def load_journal(self, journal="action.txt"):
        """
        node should not need a function for loading a journal
        in that case just use journal's load_journal function directly for that

        but in the case of a directory, can be nice to have more direct
        access to the directory's journal.
        """
        source = os.path.join(self.path, journal)
        if os.path.exists(source):
            j = Journal()
            j.from_file(source)
            return j
        else:
            #otherwise just fall back to the standard load_journal
            #j = load_journal(self.path)
            #return j
            #if load_journal behavior is wanted, just call it directly
            #this is for looking for the default action logs of a directory
            return None
        
    def scan_directory(self, recurse=False):
        """
        only create the meta data in a python object in memory
        """
        self.items = 0
        
        self.contents = os.listdir(unicode(self.path))
        for item in self.contents:
            if item not in self.ignores:
                self.items += 1
                
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
                
                if (os.path.isfile(item_path)):
                    node = File(item_path)
                    node.check_size()
                    if not self.size:
                        self.size = node.size
                    else:
                        self.size += node.size
                    self.files.append(node)
                    
                elif (os.path.isdir(item_path)):
                    #this will recurse:
                    #self.directories.append(Directory(item_path))
                    self.sub_paths.append(item_path)
                    if recurse:
                        sub_d = Directory(item_path, recurse)
                        self.size += sub_d.size
                    else:
                        #print "Not recursing; no size found for sub-directory"
                        #print item_path
                        pass
                else:
                    print "ERROR: unknown item found; not a file or directory:"
                    print item_path

        self.last_scan = datetime.now()

    def sort_by_date(self):
        dates = []
        for f in self.files:
            dates.append( (f.date(), f) )
        dates.sort()
        self.files = []
        for d in dates:
            #print d[0]
            self.files.append(d[1])

    def sort_by_paths(self, filetype=None):
        if filetype is not None:
            if (filetype == "Image"):
                paths = nodes_to_paths(self.images)
                paths.sort()
                self.images = paths_to_nodes(paths)
            elif (filetype == "Movie"):
                paths = nodes_to_paths(self.movies)
                paths.sort()
                self.movies = paths_to_nodes(paths)                
            elif (filetype == "Playlist"):
                paths = nodes_to_paths(self.playlists)
                paths.sort()
                self.playlists = paths_to_nodes(paths)                
            elif (filetype == "Sound"):
                paths = nodes_to_paths(self.sounds)
                paths.sort()
                self.sounds = paths_to_nodes(paths)                
            elif (filetype == "Log"):
                paths = nodes_to_paths(self.logs)
                paths.sort()
                self.logs = paths_to_nodes(paths)                
            elif (filetype == "Document"):
                paths = nodes_to_paths(self.documents)
                paths.sort()
                self.documents = paths_to_nodes(paths)                
            #elif (filetype == "Library"):
            #    paths = nodes_to_paths(self.libraries)
            #    paths.sort()
            #    self.libraries = paths_to_nodes(paths)                

        else:
            #recursively call self for all filetypes
            all_types = [ "Image", "Movie", "Playlist", "Sound", "Log",
                          "Document" ]
            for t in all_types:
                self.sort_by_paths(filetype=t)

            #then sort the complete file list too:
            paths = nodes_to_paths(self.files)
            paths.sort()
            self.files = paths_to_nodes(paths)                
            
            
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
        if not self.filetypes_scanned:
            for f in self.files:
                t = f.path.type()
                #multiple ifs are desired behavior here
                # (as opposed to one if with and)
                # otherwise multiple calls with same files
                # pass everything into else clause
                if (t == "Image"):
                    #this will never match since contents are now Image objects
                    #not paths
                    #if (f.path not in self.images):
                    #self.images.append(f.path)
                    self.images.append(Image(f.path))
                elif (t == "Movie"):
                    self.movies.append(File(f.path))
                elif (t == "Playlist"):
                    self.playlists.append(File(f.path))
                elif (t == "Sound"):
                    self.sounds.append(Sound(f.path))
                elif (t == "Log"):
                    self.logs.append(File(f.path))
                elif (t == "Document"):
                    self.documents.append(File(f.path))
                else:
                    #must be something else:

                    #if scan_files is called more than once,
                    #and checks above are performed at the same time,
                    #then "already in" checks makes it skip to here
                    #
                    #fixed by moving in check below
                    #if (f.path not in self.other):
                    #self.other.append(f.path)
                    self.other.append(File(f.path))

            #if we don't sort now, it will be more work to sort later
            self.sub_paths.sort()
            added_paths = []
            for d in self.sub_paths:
                #this will not catch dupes, since they will be different objects:
                #if dd not in self.directories:
                if d not in added_paths:
                    #print "ADDING: %s" % d
                    dd = Directory(d)
                    self.directories.append(dd)
                    added_paths.append(d)

            self.filetypes_scanned = True

    #rename to generate_thumbnails?        
    def make_thumbs(self):
        """
        generate thumbnails for all images in this directory
        """
        self.scan_filetypes()
            
        if len(self.images):
            for i in self.images:
                i.make_thumbs()

    def default_image(self, pick_by="random"):
        self.scan_filetypes()
            
        if len(self.images):
            j = self.load_journal("action.txt")
            if j:
                #2009.12.19 13:19:27 
                #need to generate the data association first now
                j.associate_data()

                #there is a problem if the max key is not an image
                #could happen if other media is played more frequently
                
                maxkey = j.datas.max_key()
                if maxkey:
                    maxkey = maxkey.strip()
                    altkey = os.path.join(self.path, os.path.basename(maxkey))
                else:
                    altkey = ''

                mk = Path(maxkey)
                ak = Path(altkey)
                if mk.exists():
                    if mk.type() == "Image":
                        return Image(maxkey)
                    else:
                        return self.images[0]
                    
                #maybe the path has changed in the log:
                elif ak.exists():
                    if ak.type() == "Image":
                        return Image(altkey)
                    else:
                        return self.images[0]

            elif pick_by == "random":
                random.seed()
                r = random.randint(0, len(self.images)-1)
                return self.images[r]

            #must not have found anything statistical if we make it here
            #just return the first one in the list
            return self.images[0]
        else:
            #no images to get
            return None

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
        images = self.images

        #os.system("jhead -autorot %s/*.JPG" % self.path)
        #result = os.popen("jhead -autorot %s/*.JPG" % self.path)
        #jhead = subprocess.Popen("jhead -autorot %s/*.JPG" % self.path, shell=True, stdout=subprocess.PIPE)
        #jhead.wait()
        #result = jhead.stdout.read()

        result = ''
        for i in self.images:
            jhead = subprocess.Popen("jhead -autorot %s" % i.path, shell=True, stdout=subprocess.PIPE)
            current = jhead.communicate()[0]
            #print "Finished rotating: %s, %s" % (i.name, current)
            if current: print current
            result += current

        #similar issue with thumbnails... not updated
        #for these we only want to regenerate those that changed for speed
        new_result = ''
        if update_thumbs:
            for line in result.split('\n'):
                if line:
                    (x, path) = line.split('Modified: ')
                    new_result += path + '\n'
                    i = Image(path)
                    i.make_thumbs()
                
        #can reset all image stat, even those not rotated, just to simplify task
        for i in images:
            i.reset_stats()

        return new_result

    def file_date_range(self):
        """
        generate a name based on the range of dates for files in this directory

        assumes the files array is sorted by date after initialization
        any other order may give undefined results
        """
        new_name = ''
        start = self.files[0].date()
        end = self.files[-1].date()
        if start != end:
            new_name = start + '-' + end
        else:
            new_name = start

        return new_name

    def files_to_journal(self, filetype="Image", journal_file="action.txt"):
        jpath = os.path.join(self.path, journal_file)
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

        for i in files:
            #could also use j.make_entry() here:
            #e = Moment()
            #e.created = Timestamp(i.datetime())
            #e.tags = tags
            #e.data = i.path
            #j.update_entry(e)
            j.make_entry(data=i.path, tags=tags, created=i.datetime())

        #print j
        #j.sort_entries("reverse-chronological")
        #l = Log(filename)
        #j.to_file('temp.txt')
        j.to_file(jpath, sort="reverse-chronological")

    def adjust_time(self, hours=0):
        """
        adjust the modified time of all files in the directory by the number
        of hours specified.
        """
        for f in self.files:
            f.adjust_time(hours)


def nodes_to_paths(nodes):
    """
    take a list of nodes and
    return a list of only the local paths to those nodes
    """
    new_list = []
    for n in nodes:
        new_list.append(n.path)
    return new_list

def paths_to_nodes(paths):
    """
    take a list of local paths
    return a list of nodes for each path
    """
    new_list = []
    for p in paths:
        new_list.append(make_node(p))
    return new_list

