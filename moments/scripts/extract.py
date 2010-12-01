#!/usr/bin/env python
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

this serves as an example for setting up an extraction using manager.extract_tags function

# By: Charles Brandt [code at contextiskey dot com]
# On: *2009.07.10 10:09:38 
# License:  MIT

"""

import sys, os, re

from moments.manager import extract_tags
from moments.path import Path

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
    #set this appropriately:
    source = None
    
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            usage()
        source = sys.argv[1]

    ignores = []
    #consider adding filename path tags to ignores
    #we don't really want to add or remove tags at this stage.
    ignores = Path(source).to_tags()

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
