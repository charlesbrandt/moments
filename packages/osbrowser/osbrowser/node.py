"""
*2009.10.21 16:02:00 
moved into moments.node
can also see node.py.orig in this directory

osbrowser can be deprecated now.
"""
from moments.node import *

## import os, os.path, re
## import urllib
## import random
## import subprocess

## from datetime import datetime

## from paths import *

## from moments.moment import Moment
## from moments.journal import Journal
## from moments.log import Log as MomentLog
## from moments.association import check_ignore
## from moments.tags import Tags, split_path # tags_from_string

## def local_to_relative(path=None, add_prefix=False):
##     """
##     if node is a file, this will include the filename at the end!!!
##     """
##     #want to make sure that the path we're looking at contains local_path
##     prefix = os.path.commonprefix([local_path, path])
##     if prefix == local_path:
##         #take everything after prefix as relative
##         temp_path = path[len(prefix)+1:]
##     else:
##         #not sure what was sent, might as well just give it back
##         temp_path = path

##     #if re.search(r'\\', temp_path):
##     #temp_path = re.subn(r'\\', '/', temp_path)
##     temp_path = temp_path.replace(r'\\', '/')
    
##     if add_prefix:
##         temp_path = os.path.join(config['relative_prefix'], temp_path)
##     return temp_path

## def name_only(name):
##     """
##     opposite of extension
##     """
##     #make sure there is an extension
##     new_name = ''
##     if re.search('\.', name):
##         parts = name.split('.')
##         only = parts[:-1]
##         temp = '.'.join(only)
##         new_name = temp
##     else:
##         new_name = name
##     #print new_name
##     return new_name

## def extension(name):
##     """
##     turns out that this is similar to os.path.splitext()
    
##     find a file's file extension (part of filename after last '.')

##     splitting into a list with two items:
##     prefix, extension = f.name.split(".")
##     will not work with file names with multiple '.'s in them
##     """
##     #could also check if there is a '.' in the string, return none if not
##     parts = name.split('.')
##     extension = parts[-1]
##     #print extension
##     return extension

## class Node:
##     """
##     could be a file or a directory

##     one thing connected to other things
    
##     structure to hold the meta data of a node on a filesystem
##     should hold the common attributes of files and directories

##     path that is passed in is expected to be relative

##     soon changing all Node paths to be relative to the local system...
##     i.e. how python would find them
##     """
##     def __init__(self, path):
##         self.path = unicode(path)
##         #self.path = path
##         #http://docs.python.org/lib/module-os.path.html        
##         self.name = os.path.basename(self.path)
##         if not self.name:
##             #might have been passed in a path with a trailing '/'
##             self.path = os.path.dirname(self.path)
##             self.name = os.path.basename(self.path)

##         #name without file extension:
##         self.name_only = name_only(self.name)

##         #we don't initialize this since it could be a directory
##         #should be initialized in File though
##         self.size = 0

##         #http://docs.python.org/lib/os-file-dir.html
##         stat = os.stat(self.path)
##         #st_atime (time of most recent access)
##         self.atime = stat.st_atime
##         #st_mtime (time of most recent content modification)
##         self.mtime = stat.st_mtime
##         #st_ctime (platform dependent; time of most recent metadata change on Unix, or the time of creation on Windows)
##         self.ctime = stat.st_ctime

##         self.md5 = None
##         self.last_scan = None

##     def __str__(self):
##         #this will fail if path has unicode characters it doesn't know 
##         return str(self.path)
    
##     def __unicode__(self):
##         return unicode(self.path)

##     def find_type(self):
##         """
##         determine the subclass that should be associated with this Node
##         this gives us a central place to track this
##         """

##         #PCD seems to cause a lot of trouble
##         image_extensions = [ 'jpg', 'png', 'gif', 'jpeg', 'JPG', 'tif' ]
##         movie_extensions = [ 'mpg', 'avi', 'flv', 'vob', 'wmv', 'AVI', 'iso' ]
##         playlist_extensions = [ 'm3u', 'pls' ]
##         #, 'm4p' are not playable by flash, should convert to use
##         sound_extensions = [ 'mp3', 'wav', 'aif', 'ogg' ]
##         journal_extensions = [ 'txt', 'log' ]
##         #library_extensions = [ 'xml' ]
##         document_extensions = [ 'html', 'htm', 'mako' ]
        
##         #determine what the right type of node should be based on path
##         if (os.path.isfile(self.path)):
##             ext = extension(self.name)
##             if ext in image_extensions:
##                 return "Image"
##             elif ext in movie_extensions:
##                 return "Movie"
##             elif ext in playlist_extensions:
##                 return "Playlist"
##             elif ext in sound_extensions:
##                 return "Sound"
##             elif ext in journal_extensions:
##                 return "Log"
##             #elif ext in library_extensions:
##             #    return "Library"
##             elif ext in document_extensions:
##                 return "Document"
##             else:
##                 return "File"
                
##         elif (os.path.isdir(self.path)):
##             return "Directory"
##         else:
##             return "Node"

##     def reset_stats(self):
##         """
##         some actions (like image rotate) may update the file's modified times
##         but we sometimes want to keep the original time
##         this resets them to what they were when originally initialized
##         """
##         os.utime(self.path, (self.atime, self.mtime))

##     #should just use generalized local_to_relative if needed directly
##     #*2009.03.15 22:28:06
##     #in templates, is nice to have access to it through object
##     #wrapping general one
##     def relative_path(self, add_prefix=False):
##         return local_to_relative(self.path, add_prefix)
    
##     def custom_relative_path(self, prefix=None, path=None):
##         """
##         ideally would just use routes here... heavy overlap
        
##         function to change system path to viewer path

##         if path on file system is different than path displayed by viewer
##         can change it here

##         by making it a class method, it will stay available to others

##         stub for child classes to customize how relative path is returned
##         """

##         #filename = os.path.basename(path)
##         #parent_dir_path = os.path.dirname(path)
##         #parent_dir_name = os.path.basename(parent_dir_path)
##         #return os.path.join('/image', parent_dir_name, filename)

##         if not path:
##             path = self.path

##         if prefix:
##             parts = (prefix, local_to_relative(path))
##             try:
##                 #return urllib.quote(os.path.join(prefix, local_to_relative(path)))
##                 return urllib.quote('/'.join(parts))
##             except:
##                 #return os.path.join(prefix, local_to_relative(path))
##                 return '/'.join(parts)
##         else:
##             #return urllib.quote(os.path.join('/', local_to_relative(path, add_prefix=True)))
##             return urllib.quote(''.join(['/', local_to_relative(path, add_prefix=True)]))

##     def relative_path_parts(self, path=''):
##         """
##         split the pieces up so that they can be navigated
##         """
##         parts = []
##         if not path:
##             path = self.path
##         path = local_to_relative(path)
##         os.path.join('/', path)
##         while path and path != '/':
##             (prefix, suffix) = os.path.split(path)
##             parts.insert(0, [suffix, path] )
##             path = prefix
##         return parts

##     def parent_path(self):
##         """
##         might be easier to just call the equivalent python code directly:
##         os.path.dirname(self.path)
##         """
##         return os.path.dirname(self.path)

##     def parent_part(self):
##         """
##         could consider returning actual parent here
##         return the suffix and path for the parent directory only
##         """
##         parts = self.relative_path_parts()
##         return parts[-2]

##     def parent(self):
##         """
##         return a Directory object for the current Node's parent 
##         """
##         if self.path != os.path.dirname(self.path):
##             parent_path = os.path.dirname(self.path)
##             parent = Directory(parent_path)
##             return parent
##         else:
##             #special case for root directory
##             return self

##     def context_tags(self):
##         """
##         looks at the relative path and filename to generate a list of tags
##         based on the file name and location

##         *2009.06.18 13:11:55 
##         could consider using moments.tags.path_to_tags
##         but this likely approaches the problem slightly differently
##         """
##         all_tags = []
##         rel_parent_dir = os.path.dirname(local_to_relative(self.path))
##         path_parts = split_path(rel_parent_dir)
##         #since each item in a path could be made up of multiple tags
##         #i.e work-todo
##         for p in path_parts:
##             if p:
##                 ptags = Tags().from_tag_string(p)
##                 #ptags = tags_from_string(p)
##                 for pt in ptags:
##                     if pt not in all_tags:
##                         all_tags.append(pt)
##         #name_tags = tags_from_string(self.name_only)
##         name_tags = Tags().from_tag_string(self.name_only)

##         #print "name tags: %s, name_only: %s" % (name_tags, self.name_only)
##         for nt in name_tags:
##             if nt not in all_tags:
##                 all_tags.append(nt)
##         #all_tags.extend(name_tags)
##         #print "all tags: %s" % all_tags
##         return all_tags

##     #should be load_journal  ... not really creating a new file here
##     def create_journal(self, add_tags=[]):
##         """
##         create a temporary, in memory journal from logs
        
##         this works for both directories and log files
##         """
##         #ignore_dirs = [ 'downloads', 'binaries' ]
##         ignore_dirs = [ 'downloads' ]
##         j = Journal()
##         if self.find_type() == "Directory":
##             for root,dirs,files in os.walk(self.path):
##                 for f in files:
##                     if not re.compile('.*\.txt$').search(f):
##                         continue

##                     if not check_ignore(os.path.join(root, f), ignore_dirs):
##                         #fnode = make_node(os.path.join(root, f), relative=False)
##                         #could just as easily be a Node, since that is where
##                         #context_tags() lives
##                         these_tags = add_tags[:]
##                         fnode = Node(os.path.join(root, f))
##                         filename_tags = fnode.context_tags()
##                         these_tags.extend(filename_tags)
##                         j.from_file(os.path.join(root, f), add_tags=these_tags)
##                         #fnode.log.close()

##         elif self.find_type() == "Log":
##             j.from_file(self.path, add_tags)
##             #c.entries = node.log.to_entries()
##         else:
##             #no journal to create
##             pass
##         return j

##     def move(self, rel_destination):
##         """
##         this utilizes the os.rename function
##         """
##         rel_parent = os.path.dirname(local_to_relative(self.path))
##         destination = os.path.join(local_path, rel_parent, rel_destination)
##         destination = os.path.normpath(destination)
##         #new_dir = os.path.join(image_dir, data)
##         (new_dir, new_name) = os.path.split(destination)

##         #could also use os.renames()   note plural
##         if not os.path.isdir(new_dir):
##             os.mkdir(new_dir)
##         os.rename(self.path, destination)

##     def datetime(self):
##         t = datetime.fromtimestamp(self.mtime)
##         return t

##     def day(self):
##         """
##         print creation time in a specific format
##         """
##         t = datetime.fromtimestamp(self.mtime)
##         return t.strftime("%m/%d")

##     def time(self):
##         t = datetime.fromtimestamp(self.mtime)
##         return t.strftime("%H:%M")

##     def date(self):
##         t = datetime.fromtimestamp(self.mtime)
##         return t.strftime("%Y%m%d")

##     def log_action(self, actions=["access"], data=None,
##                    log_in_media=False, log_in_outgoing=False, outgoing=None):
##         """
##         generic function for all nodes to have easy abilty to signal
##         a loggable action

##         also a good place to handle session actions if that is desired
##         behavior

##         probably won't want to handle the decision to log in calling functions
##         better left to system specific configuration files

##         to ensure this could remove:
##         log_in_media=False, log_in_outgoing=False
        
        
##         """
##         #make the entry:
##         t = datetime.now()
##         #by using make_relative_path instead of self.path, should be able
##         #to adapt to other servers if using the same structure for data
##         #(even if it is mounted elsewhere locally)
##         entry = None
##         if not data:
##             entry = Moment(local_to_relative(self.path), actions, t)
##         else:
##             entry = Moment(data, actions, t)
            
##         if config_log_in_media or log_in_media:
##             log = ''
##             if self.find_type() != "Directory":
##                 #print "ITS NOT A DIRECTORY"
##                 log = MomentLog(os.path.join(os.path.dirname(self.path), "action.txt"))
##             else:
##                 #print "ITS A DIRECTORY"
##                 log = MomentLog(os.path.join(self.path, "action.txt"))
##             log.from_file()
##             entries = log.to_entries()
##             entries.insert(0, entry)
##             log.from_entries(entries)
##             log.to_file()

##         if outgoing or config_log_in_outgoing or log_in_outgoing:
##             if not outgoing is None:
##                 destination = outgoing
##             else:
##                 destination = log_path
##             s_log = MomentLog(os.path.join(destination, t.strftime("%Y%m%d")+'.txt'))
##             s_log.from_file()
##             entries = s_log.to_entries()
##             entries.insert(0, entry)
##             s_log.from_entries(entries)
##             s_log.to_file()

## class File(Node):
##     """
##     files are Nodes with sizes
##     also leafs in tree structure
##     """
##     def __init__(self, path):
##         Node.__init__(self, path)
##         self.size = os.path.getsize(path)
##         self.last_scan = datetime.now()

## from image import Image
## from sound import Sound
## #from log import Log
## #from library import Library

## class Directory(Node):
##     """
    
##     object to hold a summary of a single directory
##     (no recursion.  one level only)

##     The important thing here is that we represent a Directory and the meta data
##     most code would need for working with a directory (without needing the
##     directory itself)

##     """
##     def __init__(self, path='', recurse=False, meta_enabled=True, **args):
##         """
##         check if there is already an index in the path
##         if so load it
##         otherwise create one.
##         """
##         Node.__init__(self, path, **args)

##         #print "initializing directory: %s" % self.path

##         self.items = 0

##         #names only!!
##         #everything
##         self.contents = []

##         #this will be a list of paths to prevent recursion
##         self.sub_paths = []
        
##         #self.ignores = []
##         self.ignores = [ '.hg', '.svn', 'index.xml', 'index.txt', 'meta.txt', 'sized', '.DS_Store', '.HFS+ Private Directory Data', '.HFS+ Private Directory Data\r', '.fseventsd', '.Spotlight-V100', '.TemporaryItems', '.Trash-ubuntu', '.Trashes', 'lost+found' ]

##         #these should be osbrowser.File python objects
##         self.files = []

##         #shouldn't really need to make a MediaList of these (too meta/recursive)

##         #maybe we do
##         #that way can return Node objects, which will help w/ rendering links
##         #Node objects should not try to perform any playlist related tasks

##         #2008.12.08 15:31:58
##         #would really like to undo the dependency on MediaLists here
##         #they should be a higher level concept, as needed
##         #but here it is really just a list of items of different types

##         #if we need node objects for rendering,
##         #then directory should have a built in way for handling this
##         #rather than pushing the issue further upstream

##         #maybe that means meta objects?
        
## ##         self.playlists = MediaList("Node")
## ##         self.sub_directories = MediaList("Directory")
## ##         self.libraries = MediaList()
## ##         #should be able to get an image by name, or get it's thumbnail
## ##         self.images = MediaList("Image", sort_order="alpha")
## ##         self.sounds = MediaList("Sound", node=self)
## ##         self.movies = MediaList()
## ##         self.logs = MediaList("Log")
## ##         self.documents = MediaList("File")
## ##         self.other = MediaList("File")

##         self.filetypes_scanned = False
##         #*2009.06.10 07:22:54 
##         #safe to just call these directories?
##         self.sub_directories = []
##         self.playlists = []
##         self.libraries = []
##         self.images = []
##         self.sounds = []
##         self.movies = []
##         self.logs = []
##         self.documents = []
##         self.other = []

##         #depending on context, might want to know the default page
##         #or might want to know the default image
##         #self.default_image = ""
##         self.default_node = ""

##         if not self.find_and_load_index():
##             self.scan_directory(recurse)

##     def find_and_load_index(self):
##         """
##         should scan path for different versions of existing indexes
##         (if one exists)
##         """
##         found = False

##         #try to load:
##         #index = "index.xml"
##         options = []
##         for o in options:
##             filename = os.path.join(self.path, o)
##             self.filename = filename

##             if os.path.isfile(filename):
##                 found = True
##                 self.tree = ElementTree.ElementTree(file=filename)
##                 self.root = self.tree.getroot()

##         return found

##     def scan_directory(self, recurse=False):
##         """
##         only create the meta data in a python object in memory
##         """
##         self.items = 0
        
##         self.contents = os.listdir(unicode(self.path))
##         for item in self.contents:
##             if item not in self.ignores:
##                 self.items += 1
                
##                 #print "SUPPORTS UNICODE: %s" % os.path.supports_unicode_filenames
##                 if os.path.supports_unicode_filenames:
##                     item_path = os.path.normpath(os.path.join(unicode(self.path), item))
##                 else:
##                     #item_path = unicode(self.path) + u'/' + unicode(item)
##                     try:
##                         item_path = os.path.normpath(os.path.join(self.path, item))
##                     except:
##                         item_path = ''
##                         print "could not open: %s" % item

##                 item_path = unicode(item_path)
                
##                 if (os.path.isfile(item_path)):
##                     node = File(item_path)

##                     self.size += node.size
##                     self.files.append(node)
                    
##                 elif (os.path.isdir(item_path)):
##                     #this will recurse:
##                     #self.sub_directories.append(Directory(item_path))
##                     self.sub_paths.append(item_path)
##                     if recurse:
##                         sub_d = Directory(item_path, recurse)
##                         self.size += sub_d.size
##                     else:
##                         #print "Not recursing; no size found for sub-directory"
##                         #print item_path
##                         pass
##                 else:
##                     print "ERROR: unknown item found; not a file or directory:"
##                     print item_path

##         self.last_scan = datetime.now()

##     def sort_by_date(self):
##         dates = []
##         for f in self.files:
##             dates.append( (f.date(), f) )
##         dates.sort()
##         self.files = []
##         for d in dates:
##             #print d[0]
##             self.files.append(d[1])

##     def sort_by_paths(self, filetype=None):
##         if filetype is not None:
##             if (filetype == "Image"):
##                 paths = nodes_to_paths(self.images)
##                 paths.sort()
##                 self.images = paths_to_nodes(paths)
##             elif (filetype == "Movie"):
##                 paths = nodes_to_paths(self.movies)
##                 paths.sort()
##                 self.movies = paths_to_nodes(paths)                
##             elif (filetype == "Playlist"):
##                 paths = nodes_to_paths(self.playlists)
##                 paths.sort()
##                 self.playlists = paths_to_nodes(paths)                
##             elif (filetype == "Sound"):
##                 paths = nodes_to_paths(self.sounds)
##                 paths.sort()
##                 self.sounds = paths_to_nodes(paths)                
##             elif (filetype == "Log"):
##                 paths = nodes_to_paths(self.logs)
##                 paths.sort()
##                 self.logs = paths_to_nodes(paths)                
##             elif (filetype == "Document"):
##                 paths = nodes_to_paths(self.documents)
##                 paths.sort()
##                 self.documents = paths_to_nodes(paths)                
##             #elif (filetype == "Library"):
##             #    paths = nodes_to_paths(self.libraries)
##             #    paths.sort()
##             #    self.libraries = paths_to_nodes(paths)                
##             else:
##                 pass
            
##     def scan_filetypes(self):
##         """
##         look in the directory's list of files for different types of files
##         put them in the right list type in the directory

##         should have already scanned the directory for files

##         we will look through the list of files
##         for files that are likely images
##         then populate that list


##         not sure if this should always happen at scan time
##         what if we don't need to use images, sounds, movies?  extra step
##         maybe only create special node types if they're needed. 
        
##         depending on the file extension, should create an object
##         with the appropriate type
##         and add it to the correct list in the Directory
        
##         """

## ##         self.images = MediaList("Image", sort_order="alpha")
## ##         self.movies = MediaList()
## ##         self.playlists = MediaList("Node")
## ##         self.sounds = MediaList("Sound", node=self)
## ##         self.logs = MediaList("Log")
## ##         self.documents = MediaList("File")
## ##         self.libraries = MediaList()
## ##         self.other = MediaList("File")
## ##         self.sub_directories = MediaList("Directory")
        
##         # we should only need to scan the filetypes once per instance:
##         if not self.filetypes_scanned:
##             for f in self.files:
##                 t = f.find_type()
##                 #multiple ifs are desired behavior here
##                 # (as opposed to one if with and)
##                 # otherwise multiple calls with same files
##                 # pass everything into else clause
##                 if (t == "Image"):
##                     #this will never match since contents are now Image objects
##                     #not paths
##                     #if (f.path not in self.images):
##                     #self.images.append(f.path)
##                     self.images.append(Image(f.path))
##                 elif (t == "Movie"):
##                     #if (f.path not in self.movies):
##                     #self.movies.append(f.path)
##                     self.movies.append(File(f.path))
##                 elif (t == "Playlist"):
##                     #if (f.path not in self.playlists):
##                     #self.playlists.append(f.path)
##                     self.playlists.append(File(f.path))
##                 elif (t == "Sound"):
##                     #if (f.path not in self.sounds):
##                     #self.sounds.append(f.path)
##                     self.sounds.append(Sound(f.path))
##                 elif (t == "Log"):
##                     #if (f.path not in self.logs):
##                     #self.logs.append(f.path)
##                     #self.logs.append(MomentLog(f.path))
##                     self.logs.append(File(f.path))
##                 elif (t == "Document"):
##                     #if (f.path not in self.documents):
##                     #self.documents.append(f.path)
##                     self.documents.append(File(f.path))
##                 #elif (t == "Library"):
##                 #    #if (f.path not in self.libraries):
##                 #    #self.libraries.append(f.path)
##                 #    self.libraries.append(File(f.path))
##                 else:
##                     #must be something else:

##                     #if scan_files is called more than once,
##                     #and checks above are performed at the same time,
##                     #then "already in" checks makes it skip to here
##                     #
##                     #fixed by moving in check below
##                     #if (f.path not in self.other):
##                     #self.other.append(f.path)
##                     self.other.append(File(f.path))

##             #if we don't sort now, it will be more work to sort later
##             self.sub_paths.sort()
##             added_paths = []
##             for d in self.sub_paths:
##                 #this will not catch dupes, since they will be different objects:
##                 #if dd not in self.sub_directories:
##                 if d not in added_paths:
##                     #print "ADDING: %s" % d
##                     dd = Directory(d)
##                     self.sub_directories.append(dd)
##                     added_paths.append(d)

##             self.filetypes_scanned = True

##     #rename to generate_thumbnails?        
##     def make_thumbs(self):
##         """
##         generate thumbnails for all images in this directory
##         """
##         self.scan_filetypes()
            
##         if len(self.images):
##             for i in self.images:
##                 i.make_thumbs()

    


##     def default_image(self, pick_by="random"):
##         self.scan_filetypes()
            
##         if len(self.images):
##             action_log = os.path.join(self.path, "action.txt")
##             #by not checking pick_by, action logs will always be evaluated
##             #then can fall back to other method.
##             if os.path.exists(action_log):
##                 #sort / analyze meta here for best candidate
##                 j = Journal()
##                 j.from_file(action_log)

##                 #there is a problem if the max key is not an image
##                 #could happen if other media is played more frequently
                
##                 #maxkey = j.datas.max_key().strip()
##                 maxkey = j.datas.max_key()
##                 if maxkey:
##                     maxkey = maxkey.strip()
##                     altkey = os.path.join(self.path, os.path.basename(maxkey))
##                 else:
##                     altkey = ''
                    
##                 if os.path.exists(maxkey):
##                     #print "Max Key: %s" % maxkey
##                     #node = make_node(maxkey)
##                     node = Node(maxkey)
##                     if node.find_type() == "Image":
##                         return Image(maxkey)
##                     else:
##                         return self.images[0]
##                 #maybe the path has changed in the log:
##                 elif os.path.exists(altkey):
##                     #node = make_node(altkey, relative=False)
##                     node = Node(altkey)
##                     if node.find_type() == "Image":
##                         return Image(altkey)
##                     else:
##                         return self.images[0]

##             elif pick_by == "random":
##                 random.seed()
##                 r = random.randint(0, len(self.images)-1)
##                 #return self.images.get_object(self.images[r])
##                 return self.images[r]

##             #must not have found anything statistical if we make it here
##             #just return the first one in the list
##             return self.images[0]
##         else:
##             #no images to get
##             return None

##     def auto_rotate_images(self, update_thumbs=True):
##         """
##         #it's best to just use:
##         jhead -autorot *.JPG

##         this resets the last modified timestamp to now()
##         not what we want, so go through and reset all timestamps
##         to original times

##         http://www.sentex.net/~mwandel/jhead/
##         """
##         self.scan_filetypes()
##         #image_list = self.get_images()
##         #images = image_list.as_objects()
##         images = self.images

##         #os.system("jhead -autorot %s/*.JPG" % self.path)
##         #result = os.popen("jhead -autorot %s/*.JPG" % self.path)
##         #jhead = subprocess.Popen("jhead -autorot %s/*.JPG" % self.path, shell=True, stdout=subprocess.PIPE)
##         #jhead.wait()
##         #result = jhead.stdout.read()

##         result = ''
##         for i in self.images:
##             jhead = subprocess.Popen("jhead -autorot %s" % i.path, shell=True, stdout=subprocess.PIPE)
##             current = jhead.communicate()[0]
##             #print "Finished rotating: %s, %s" % (i.name, current)
##             if current: print current
##             result += current
            
            

##         #similar issue with thumbnails... not updated
##         #for these we only want to regenerate those that changed for speed
##         new_result = ''
##         if update_thumbs:
##             for line in result.split('\n'):
##                 if line:
##                     (x, path) = line.split('Modified: ')
##                     new_result += path + '\n'
##                     i = Image(path)
##                     i.make_thumbs()
                
##         #can reset all image stat, even those not rotated, just to simplify task
##         for i in images:
##             i.reset_stats()

##         return new_result

##     def file_date_range(self):
##         """
##         generate a name based on the range of dates for files in this directory

##         assumes the files array is sorted by date after initialization
##         any other order may give undefined results
##         """
##         new_name = ''
##         start = self.files[0].date()
##         end = self.files[-1].date()
##         if start != end:
##             new_name = start + '-' + end
##         else:
##             new_name = start

##         return new_name

## def make_node(path='', node_type=None, relative=True, create=True, local_path=local_path):
##     """
##     take either a relative or absolute path
##     looks at the path,
##     determines the right kind of node to associate with that path
##     returns the node

##     [2008.11.18 19:47:46]
##     might be a way to do this with meta classes

##     looks like this is a bit of a class factory

##     suggestions welcome!
##     """
##     if relative:
##         actual_path = os.path.join(unicode(local_path), path)
##         #actual_path = unicode(os.path.join(local_path, path))
##     else:
##         actual_path = path

##     actual_path = unicode(actual_path)
##     actual_path = os.path.normpath(actual_path)

##     new_node = None
##     if (create and not os.path.exists(actual_path) and
##         extension(actual_path) == "txt"):
##         #only want to create new log files, and then only if logging
##         #is enabled
##         #should be equivalent to a touch
##         f = file(actual_path, 'w')
##         f.close()

##     #to skip throwing an error if no file exists, uncomment following:
##     #if os.path.exists(actual_path):
##     if not node_type:
##         new_node = Node(actual_path)
##         node_type = new_node.find_type()
##         if node_type in [ "Playlist", "Movie", "Document", "Library", "Log" ]:
##             #special case
##             node_type = "File"
            
##     #ah ha!  passing in path as unicode is very important if planning to work
##     #with unicode paths... otherwise gets converted to ascii here:
##     #new_node = eval("%s(u'%s')" % (node_type, actual_path))
##     #above is causing trouble on windows, trying without

##     #node_create = "%s(r'%s')" % (node_type, actual_path)
##     #node_create = r'%s("%s")' % (node_type, actual_path)
##     #re.subn(r"\\", r"\\\\", node_create)
##     #new_node = eval(node_create)

##     #2008.12.23 14:18:59
##     #eval having a hard time with windows.  switching to a nested if-else:
##     if node_type == "Node":
##         #new_node already defined:
##         pass
##     elif node_type == "Directory":
##         new_node = Directory(actual_path)
##     elif node_type == "Image":
##         new_node = Image(actual_path)
##     elif node_type == "Sound":
##         new_node = Sound(actual_path)
##     else:# node_type == "File":
##         new_node = File(actual_path)

##     return new_node

## def nodes_to_paths(nodes):
##     """
##     take a list of nodes and
##     return a list of only the local paths to those nodes
##     """
##     new_list = []
##     for n in nodes:
##         new_list.append(n.path)
##     return new_list

## def paths_to_nodes(paths):
##     """
##     take a list of local paths
##     return a list of nodes for each path
##     """
##     new_list = []
##     for p in paths:
##         new_list.append(make_node(p))
##     return new_list

