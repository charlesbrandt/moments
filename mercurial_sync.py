#!/usr/bin/env python
"""
#
# Description:
  Script to run through the process
  of synchronizing mulitple mercurial repositories
  probably similar in goal to a mercurial forest
  but just loops over all repositories available
  
# By: Charles Brandt [code at contextiskey dot com]
# On: *2010.01.30 19:47:05
#     also [2010.03.01 09:26:01] 
# License:  MIT 

# Requires: mercurial
#

This was adapted from a collection of shell scripts that would approximate this behavior using the mercurial command line interface:
export PATH1=/c
export PATH2=/media/CHARLES

cd $PATH1/charles
hg stat
cd $PATH2/charles
cd -
hg pull $PATH2/charles
hg push $PATH2/charles

*2010.01.31 13:38:04
todo:
consider a
stat-all command

could then configure what meta action to take
and also the different roots from command line

# newer versions of mercurial require a .hg/hgrc file with an appropriate user configuration to be present.
  File "/Library/Frameworks/Python.framework/Versions/2.5/lib/python2.5/site-packages/mercurial/ui.py", line 189, in username
    raise util.Abort(_('no username supplied (see "hg help config")'))
mercurial.error.Abort: no username supplied (see "hg help config")
"""

import os, re, sys
from mercurial import ui, hg, commands

def sync_repos(local_root='/c', remote_root='/media/charles/CHARLES'):
    #local_root = '/c'
    #remote_root = '/media/CHARLES'

    interface = ui.ui()

    local_options = os.listdir(local_root)
    local_options.sort()
    remote_options = os.listdir(remote_root)
    remote_options.sort()

    #*2010.05.03 22:24:10 
    #not sure that this line is needed... certainly causes problems if there
    #is only one directory locally:
    #o = local_options[1]
    for o in local_options:
        if os.path.exists(os.path.join(local_root, o, '.hg')):
            #print "%s is a mercurial repository" % o
            local_repo_path = os.path.join(local_root, o)
            if o in remote_options:
                print "'%s' is on remote media, preparing to sync..." % o
                remote_repo_path = os.path.join(remote_root, o)

                #first pull down any changes that may exist on remote
                repo = hg.repository(interface, local_repo_path)
                interface.pushbuffer()
                commands.pull(interface, repo, remote_repo_path)
                result = interface.popbuffer()
                #doesn't seem that the interface will catch all of the output of a pull
                #if there were changes pull, it does get the line:
                #(run 'hg update' to get a working copy)
                #
                #if not, only has:
                # pulling from /media/CHARLES/charles

                #keep track if we find something that changes
                #so that we can pause at the end
                #otherwise we should just move on automatically
                changes = False

                print "%s" % result
                lines = result.splitlines()
                if len(lines) > 1:
                    changes = True
                    if re.search('hg update', lines[1]):
                        print "updating"
                        interface.pushbuffer()
                        commands.update(interface, repo)
                        result = interface.popbuffer()
                        print "%s" % result
                        response = interface.prompt("everything ok? (ctl-c to exit)",
                                                    default='y')
                        print "moving on then..."

                    else:
                        #must be a merge:
                        print "merge detected, all yours:"
                        print "cd %s" % local_repo_path
                        exit()

                #at this point all changes from remote media should be applied locally
                #now we should check if we have any changes here:
                interface.pushbuffer()
                commands.status(interface, repo)
                result = interface.popbuffer()
                if result:
                    print "looks like there are some local changes:"
                    print result
                    changes = True

                    new_files = False
                    for line in result.splitlines():
                        if line.startswith('?'):
                            new_files = True
                    if new_files:
                        print "new files found"
                        response = interface.prompt("would you like to add the new files?", default='y')
                        if response == 'y':
                            commands.add(interface, repo)


                    response = interface.prompt("log (ctl-c to exit):", default='')
                    commands.commit(interface, repo, message=response)

                #push changes:
                print "hg push %s" % remote_repo_path
                commands.push(interface, repo, remote_repo_path)

                lines = result.splitlines()
                if len(lines) > 1:
                    changes = True
                #on remote repo,
                remote_repo = hg.repository(interface, remote_repo_path)
                #update
                print "updating remote:"
                interface.pushbuffer()
                commands.update(interface, remote_repo)
                result = interface.popbuffer()
                print "%s" % result

                #show remote status
                commands.status(interface, remote_repo)

                if changes:
                    response = interface.prompt("everything ok? (ctl-c to exit)",
                                                default='y')


            else:
                print "%s is not on remote media, skipping" % o

        else:
            #print "skipping: %s" % o
            pass

def usage():
    print ""
    print ""
    print "python /c/moments/moments/export.py /c/outgoing/ /media/CHARLES/outgoing/"
    print "python /c/moments/moments/export.py /c/outgoing/ /media/charles/CHARLES/outgoing/"

    print "(reset any open journal buffers after export)"
    print ""
    print "/c/moments/mercurial_sync.py /c/clients /media/CHARLES/clients"    
    print "/c/moments/mercurial_sync.py /c/clients /media/WORK/clients"    
    print "/c/moments/mercurial_sync.py /c /media/WORK/"
    print ""
    print "/c/moments/mercurial_sync.py /c /media/CHARLES/"

def main():
    if len(sys.argv) > 1:
        helps = ['--help', 'help', '-h']
        for i in helps:
            if i in sys.argv:
                usage()
                exit()

        #skip the first argument (filename):
        #if only one argument, assume it is a different remote root
        #if there are two, assume that:
        #    the first is a different local_root
        #    the second is a different remote_root
        args = sys.argv[1:]
        if len(args) > 1:
            sync_repos(local_root=args[0], remote_root=args[1])
        elif len(args) == 1:
            sync_repos(remote_root=args[0])
        else:
            print "SHOULDN'T BE HERE"
            exit()
    else:
        #go with the default here
        sync_repos()
        
if __name__ == '__main__':
    main()
    usage()
    #read_file("some_file.txt")

    #finish by printing export and extract commands:
    #(from /c/charles/system/merge-usb.txt)

    ## repo = hg.repository(interface, '.')
    ## interface.pushbuffer()
    ## commands.status(interface, repo)
    ## status = interface.popbuffer()
    ## print "->%s<-" % status

    #getting user input:
    #response = interface.prompt("what?", default='y')
    #print response
