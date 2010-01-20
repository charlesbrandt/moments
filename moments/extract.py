#!/usr/bin/env python
"""
#
# Description:
# take a list of tags,
# and the directory or file that you want to use as the source of the tags
# go through all files, and remove those tags
# saving them in a new separate file (or specified existing file)

# adapted from pose.controllers.tags.extract

# By: Charles Brandt [code at contextiskey dot com]
# On: *2009.07.10 10:09:38 
# License:  MIT

*2009.08.29 13:20:46
now part of the moments module itself

not to be confused with the Journal.extract method
these functions are higher level operations that utilize Journal.extract
"""

import sys, os, re
from datetime import datetime
from journal import load_journal, Journal
from timestamp import Timestamp
from tags import Tags, path_to_tags
from association import check_ignore, filter_list
from ascii import unaccented_map

class ExtractConfig(object):
    """
    used in /c/charles/system/extract_config.py
    """
    def __init__(self):
        self.sources = ''
        self.ignores = ''
        self.extractions = []
        self.name = ''
        
## def extract_one(tags, path, extract_type):

##     these_tags = []
##     filename_tags = path_to_tags(path)
##     these_tags.extend(filename_tags)
##     j = Journal()
##     j.from_file(path, add_tags=these_tags)
##     entries = j.extract(tags, extract_type)
##     #when it's time to save:
##     #j.to_file()
##     return entries

## def extract_tag(path, tag_string, extract_type='intersect'):
##     """
##     extract one tag from many files
    
##     for merging, see admin controller in pose
##     could be tricky with only one file to specify
##     might need to use command line for this for now

##     for each file in fpath
##     add any entry that matches tag_string criteria
##     to a local buffer
##     [local buffer will need to be a static (pre-configured) path
##      since we only have one variable path to work with,
##      and that needs to be the source
##      we can generate the output filename based on date and tags extracted
##      ]

##     and save original/source journal/log file without the extracted entries

##     very similar to Node->create_journal() or moments.journal.load_journal()
##     but we are doing a different action on each file (_extract_one)
##     so they need to stay separate
##     """

##     extracts = Journal()

##     tags = Tags().from_tag_string(tag_string)

##     add_tags = []
##     ignore_dirs = [ 'downloads', 'binaries' ]
##     log_check = re.compile('.*\.txt$')
##     if os.path.isdir(path):
##         for root,dirs,files in os.walk(path):
##             for f in files:
##                 if not log_check.search(f):
##                     continue
                
##                 cur_file = os.path.join(root, f)
##                 if not check_ignore(cur_file, ignore_dirs):
##                     entries = extract_one(tags, cur_file, extract_type)
##                     print "%s entries found in %s" % (len(entries), path)
##                     extracts.from_entries(entries)
                        
##     elif os.path.isfile(path) and log_check.search(path):
##         entries = extract_one(tags, path, extract_type)
##         print "%s entries found in %s" % (len(entries), path)
##         extracts.from_entries(entries)
##     else:
##         #no journal to create
##         pass

##     if len(extracts):
##         #now that we've extracted everything
##         #save the extracts journal to a log
##         t = datetime.now()
##         now = t.strftime("%Y%m%d%H%M%S")
##         fname = now + '-' + tag_string + '.txt'
##         #dest = os.path.join(config['log_local_path'], fname)
##         print "saving %s entries to %s" % (len(extracts), fname)
##         extracts.to_file(fname)

##         #could gather print statements to have something to return here:
##         #return output

##         return fname
##     else:
##         print "nothing extracted"

def extract_many(path, extractions, ignores=[], save=False, extract_type="intersect"):
    """
    rather than go through all files for every extraction
    it is nice to go through all extractions during each file

    save extractions for each file
    rather than accumulating until end

    will make it trickier for trial runs
    can print actions or make temp logs
    """
    these_tags = []
    filename_tags = path_to_tags(path)
    #print filename_tags
    filename_tags = filter_list(filename_tags, ignores, search=True)
    #print filename_tags
    these_tags.extend(filename_tags)

    if not os.path.isfile(path):
        raise ValueError, "path must be a file, got: %s" % path
    j = Journal()
    
    #j.from_file(path, add_tags=these_tags)
    #can add tags to the export, but don't want to add them in here:
    has_entries = j.from_file(path)
    for (tags, destination) in extractions:
        entries = j.extract(tags, extract_type)
        if len(entries):
            print "found %s entries with tag: %s in: %s" % (len(entries), tags, path)
            entries.reverse()
            j2 = Journal()
            j2.from_file(destination)
            for e in entries:
                e.tags.extend(these_tags)
                j2.update_entry(e, 0)
                entry = e.render()
                e_ascii = entry.translate(unaccented_map()).encode("ascii", "ignore")
                print "adding entry to: %s\n%s" % (destination, e_ascii)
            if save:
                #this way we're saving any entries we extract to the new
                #destination before we save the original source file
                #
                #if there are permission problems writing the source file
                #at worst we'll have 2 copies of the same entry
                # (and that can be filtered out later)
                j2.to_file()

    # do *not* want to save if the file passed to the journal did not get parsed as having entries
    # this would result in a blank file being saved, resulting in data loss.
    # i.e. check both if save is desired ('save' variable)
    # and if journal had entries ('has_entries' variable)
    if save and has_entries:
        #when it's time to save:
        j.to_file()

def extract_tags(path, extractions=[], ignores=[], save=False,
                 extract_type='intersect'):
    """
    accept a list of extractions
    where each extraction consists of a set of tags to look for
    (using extract_type)
    and a destination where matching entries should be extracted to

    ignores is a list of tags to leave out of the found entries
    (good for filtering tags generated from the original file path)
    
    this duplicates the logic for scanning all files from extract_tag
    it feels more readable to separate the two
    """
    
    add_tags = []
    ignore_dirs = [ 'downloads', 'binaries' ]
    log_check = re.compile('.*\.txt$')
    if os.path.isdir(path):
        for root,dirs,files in os.walk(path):
            for f in files:
                if not log_check.search(f):
                    continue
                
                cur_file = os.path.join(root, f)
                if not check_ignore(cur_file, ignore_dirs):
                    extract_many(cur_file, extractions, ignores, save,
                                 extract_type)
                        
    elif os.path.isfile(path) and log_check.search(path):
        extract_many(path, extractions, ignores, save, extract_type)
    else:
        #no logs to scan
        print "Unknown filetype sent as path: %s" % path

    #print "finished extracting multiple tags to multiple destinations"

def main():
    """
    it is probably easier to call extract_tags in a separate script
    where all of the configuration options are defined
    there are too many to make it easy to pass on a command line
    """
    source = None
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            usage()
        source = sys.argv[1]
        
    #see:
    #/c/code/python/scripts/tests/test_extract.py
    #for usage examples

    #extract_tags may be difficult to call directly 
    #from the command-line without using a second file
    #to store the extractions mappings we want to use

    ignores = []

    extractions = [
        #(["tag"], "/path/to/destination.txt"),
        #([""], ),
        #([""], ),
        #([""], ),
        ]
    
    sys.path.append(os.getcwd())
    if not extractions:
        #can put the above list in a separate file
        from extract_config import extractions

    if not ignores:
        #can put the above list in a separate file
        from extract_config import ignores

    if source is None:
        from extract_config import source

    #print extractions
    #print source
    extract_tags(source, extractions, ignores, save=True)

def extract_completes():
    """
    Completed items in a todo list are a good example
    (and a special case)
    where many of the parameters are known,
    or can be algorithmically determined.

    """
    source = None
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            usage()
        source = sys.argv[1]

    ignores = []
    #consider adding filename path tags to ignores
    #we don't really want to add or remove tags at this stage.
    ignores = path_to_tags(source)

    #look at the source,
    #the prefix path should be the same (dirname)
    path_prefix = os.path.dirname(source)
    filename = os.path.basename(source)
    if filename == "todo.txt":
        dfilename = "journal.txt"
    elif re.search('todo', filename):
        parts = filename.split('-todo')
        prefix = parts[0]
        dfilename = prefix + '.txt'
    else:
        print "unknown todo file: %s" % source
        #could manually set it here
        #or set up script to handle passing something in
        dfilename = None
        exit()
    
    destination = os.path.join(path_prefix, dfilename)
    extractions = [
        (["complete"], destination),
        (["completed"], destination),
        ]
    extract_tags(source, extractions, ignores, save=True)
    

if __name__ == '__main__':
    #main()
    extract_completes()
