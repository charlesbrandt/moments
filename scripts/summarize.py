#!/usr/bin/env python
"""
#
# Description:
# take a directory to summarize
# create a new log file where everything is combined
# closely related to merge_logs

# By: Charles Brandt [code at contextiskey dot com]
# On: *2009.11.07 11:44:26 
# License:  MIT

# Requires: moments
"""

import sys, os
from moments.journal import Journal, load_journal
from moments.timestamp import Timestamp
from moments.node import File
from launcher import emacs

def summarize(source, destination='', add_tags=[]):
    """
    use load journal to load the source directory
    then save the resulting journal to the temporary destination
    """
    j = load_journal(source, add_tags, include_path_tags=False)
    j2 = j.sort_entries('reverse-chronological')
    print len(j)
    print len(j2)
    if not destination:
        now = Timestamp(now=True)
        temp_name = "summary-%s.temp" % (now.compact())
        #destination = os.path.join(os.path.dirname(f2), temp_name)
        destination = temp_name
    print "SAVING as: %s\n" % destination
    #j2.to_file(destination, include_path=True)
    j2.to_file(destination)

    #would be good to load all entries from /c/charles/journal.txt
    #into this month
    #eventually journal should always end up with only items for current month
    j_auto = load_journal('/c/charles/journal.txt', include_path_tags=False)
    

    node = File(destination)
    print "%s bytes found!" % node.size
    
    #add a message that this is a temporary file only!
    #(that should also make it not parseable as a log)
    ## f = open(destination)
    ## buff = f.read()
    ## f.close()
    ## f = open(destination, 'w')
    ## buff = "TEMPORARY FILE ONLY! DO NOT EDIT!\n\n" + buff
    ## f.write(buff)
    ## f.close()

    # we may want to use the new version as the definitive one
    print "ENTRIES NOW LIVE IN TWO PLACES."
    print "YOU SHOULD ONLY USE ONE VERSION AND ARCHIVE/REMOVE THE OTHER"

    #use launcher to launch editor to view summary
    files = []
    #can manually add files here
    files.append(destination)
    file_string = ' '.join(files)
    print emacs(file_string)
    
def main():
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            usage()
        f1 = sys.argv[1]
        try:
            f2 = sys.argv[2]
        except:
            f2 = ''
        summarize(f1, f2)
        
if __name__ == '__main__':
    main()
