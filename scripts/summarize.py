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

Usage:
python /c/moments/scripts/summarize.py /c/outgoing/summarize/journal/2009/10/

TODO:
also [2009.11.11 11:02:33] todo 20091111
could remove daily mention of priority from summarized log
changes to these are stored in the priorities.txt file

could also just keep all entries as days
pull in the relevant entries from journals
and then make sure each day is organized chronologically
"""

import sys, os
from moments.journal import Journal, load_journal
from moments.timestamp import Timestamp
from moments.node import File
from moments.launcher import emacs

def summarize(source, destination='', add_tags=[]):
    """
    use load journal to load the source directory
    then save the resulting journal to the temporary destination
    """
    month = 10
    year = 2009
    
    j = load_journal(source, add_tags, include_path_tags=False)

    #load all entries from /c/charles/journal.txt into this summary
    #eventually journal should always end up with only items for current month
    j_auto = load_journal('/c/charles/journal.txt', include_path_tags=False)

    #TODO:
    #would be good to determine these based on the month, context that we're
    #summarizing:
    #calculate next month
    #then subtract one second
    start = Timestamp(compact="200910")
    end = Timestamp(compact="20091031235959")

    print "j_auto pre-limit length: %s" % len(j_auto)
    matches = j_auto.limit(start.datetime, end.datetime)
    j_auto.remove_entries(matches)
    print "j_auto post-limit length: %s" % len(j_auto)
    #add found entries in:
    j.from_entries(matches)

    #sort and save what we've found
    j2 = j.sort_entries('chronological')
    print "following lengths should be the same, just sorted:"
    print len(j)
    print len(j2)
    if not destination:
        now = Timestamp(now=True)
        temp_name = "%s%s-combined.temp" % (year, month)
        #destination = os.path.join(os.path.dirname(f2), temp_name)
        destination = temp_name
    print "SAVING as: %s\n" % destination
    #j2.to_file(destination, include_path=True)
    j2.to_file(destination)

    #save j_auto here after entries have been successfully applied to new j2
    j_auto.to_file()
    
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

    #a new file for summarizing the month
    summary_name = "%s%s-summary.txt" % (year, month)
    f = open(summary_name, 'w')
    buff = "Summary for %s, %s" % (month, year)
    f.write(buff)
    #TODO: prepopulate with all days timestamps
    f.close()

    # we may want to use the new version as the definitive one
    print "WARNING!!!"
    print "ENTRIES NOW LIVE IN TWO PLACES."
    print "YOU SHOULD ONLY USE ONE VERSION AND ARCHIVE/REMOVE THE OTHER"

    #use launcher to launch editor to view summary
    files = []
    #can manually add files here
    files.append(destination)
    files.append(summary_name)
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
