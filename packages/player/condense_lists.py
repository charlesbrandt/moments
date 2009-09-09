#!/usr/bin/env python
"""
# Description:

# parse a file with -ss #### commands
# condense to python video.py -sl commands
# this way can work in either direction and not duplicate efforts

# By: Charles Brandt [code at contextiskey dot com]
# On: *2009.05.01 13:49:40 
# License:  MIT

*2009.04.30 15:44:33
have movies
made up of movie files
and a movie file can have a collection of movie marks

movie marks can be split out into separate collections
requireing the mark and the movie file to be paired

ties in with
osbrowser.node.movie
media list (with special addition for marks)

*2009.04.30 12:57:17
should split each block
and either generate the -sl list from it

or can also merge all tags together
(and eventually export/copy those to the corresponding individual log)
"""
import sys,os,re

def condense_lists(f1, f2=None, save=False):
    """
    this will regenerate the original file inserting the new commands in it
    unless f2 is specified
    """
    #TODO:
    #could ignore blocks that already have a -sl associated with them
    check_for_existing_sl = False

    result = ''

    sls = []
    last_content = ''
    last_tag = ''
    jumps = []
    f = open(f1)
    for line in f.readlines():
        if re.search("-ss", line):
            parts = line.split(" ", 2)
            #see if we're still working with the same media file:
            if parts[2] != last_content:
                #something new
                
                #make sure we had something (i.e. not first update)
                if last_content:
                    sl = "%s# -sl %s %s\n" % (last_tag, ','.join(jumps), last_content)
                    result += sl
                    sls.append(sl)
                last_content = parts[2]
                jumps = [ parts[1] ]
            else:
                jumps.append(parts[1])

        elif re.match("^\*", line):
            print "found tag line: %s" % line
            last_tag = line
        #go ahead and recreate the file
        result += line

    f.close()

    #get the last one, won't be any other trigger
    if jumps:
        sl = "# -sl %s %s\n" % (','.join(jumps), last_content)
        result += sl
        sls.append(sl)

    #print sls
    
    #save?
    if save:
        if not f2:
            #reopen it for (over)writing
            f2 = f1
        f = open(f2, 'w')
        f.write(result)
        f.close()

    return sls

def main():
    if len (sys.argv) > 1:
        if sys.argv[1] in ['--help','help'] or len(sys.argv) < 2:
            usage()
        path = sys.argv[1]

        merge_all = True
        if os.path.isdir(path):
            sls = []
            #look for all files in the directory that contain edit lists (.txt)
            #parse each of those:
            print "scanning path: %s" % path
            files = os.listdir(unicode(path))
            for f in files:
                extension = os.path.splitext(f)[1]
                fpath = os.path.join(path, f)                
                if extension == ".txt":
                    print "scanning file: %s, with extension: %s" % (fpath, extension)
                    #this will not save in the file itself
                    #result = condense_lists(fpath)
                    #this will save in each file
                    result = condense_lists(fpath, save=True)

                    sls.extend(result)

            if merge_all:
                output = open("temp.txt", 'w')
                output.writelines(sls)
            
        else:
            condense_lists(path, save=True)
        
if __name__ == '__main__':
    main()
