#!/usr/bin/env python
"""
#
# Description:
  Script to run through the process
  of synchronizing mulitple repositories under version control
  loops over all repositories available in source directory
  and compares the status of the corresponding directory in the destination
  
# By: Charles Brandt [code at contextiskey dot com]
# On: *2010.01.30 19:47:05
#     also [2010.03.01 09:26:01]
#     also [2016.12.10 07:57:19]
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

def sync_hg(hg_interface, local_repo_path, remote_repo_path):
    if not os.path.exists(remote_repo_path):
        #remote_repo_path does not exist
        #could sync with default source (e.g. github) here
        remote_repo_path = None
        
    if remote_repo_path:
        #first pull down any changes that may exist on remote
        repo = hg.repository(hg_interface, local_repo_path)
        hg_interface.pushbuffer()
        commands.pull(hg_interface, repo, remote_repo_path)
        result = hg_interface.popbuffer()
        #hg_interface won't catch all of the output of a pull
        #if there were changes in the pull, it gets the line:
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
            #changes = True
            need_update = False

            for line in lines:
                #sometimes might be only 2 lines
                #sometimes might be 3:
                #['pulling from /media/charles/CHARLES/moments', 'updating bookmark master', "(run 'hg update' to get a working copy)"]
                if re.search('hg update', line):
                    print "updating"
                    hg_interface.pushbuffer()
                    commands.update(hg_interface, repo)
                    result = hg_interface.popbuffer()
                    print "%s" % result
                    response = hg_interface.prompt("everything ok? (ctl-c to exit)",
                                                default='y')
                    print "moving on then..."
                    need_update = True

            if not need_update:
                #if we didn't update, the lines must be telling us
                #something else needs to happen...
                #must be a merge:
                print lines
                print "merge detected, all yours:"
                print "cd %s" % local_repo_path
                exit()

        #at this point all changes from remote media should be applied locally
        #now we should check if we have any changes here:
        hg_interface.pushbuffer()
        commands.status(hg_interface, repo)
        result = hg_interface.popbuffer()
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
                response = hg_interface.prompt("would you like to add the new files?", default='y')
                if response == 'y':
                    commands.add(hg_interface, repo)


            response = hg_interface.prompt("log (ctl-c to exit):", default='')
            commands.commit(hg_interface, repo, message=response)

        #push changes:
        print "hg push %s" % remote_repo_path
        commands.push(hg_interface, repo, remote_repo_path)

        lines = result.splitlines()
        if len(lines) > 1:
            changes = True
        #on remote repo,
        remote_repo = hg.repository(hg_interface, remote_repo_path)
        #update
        print "updating remote:"
        hg_interface.pushbuffer()
        commands.update(hg_interface, remote_repo)
        result = hg_interface.popbuffer()
        print "%s" % result

        #show remote status
        commands.status(hg_interface, remote_repo)

        if changes:
            response = hg_interface.prompt("everything ok? (ctl-c to exit)",
                                        default='y')
    else:
        print "skipping: %s (no remote repo detected)" % remote_repo_path
        #pass
    

def sync_repos(local_root='/c', remote_root='/media/charles/CHARLES'):
    #local_root = '/c'
    #remote_root = '/media/CHARLES'

    hg_interface = ui.ui()

    if not os.path.exists(local_root):
        print "Could not find source path: %s" % local_path
        exit()
        
    local_options = os.listdir(local_root)
    local_options.sort()

    remote_options = []
    if os.path.exists(remote_root):
        remote_options = os.listdir(remote_root)
        remote_options.sort()
    else:
        #we can try synchronizing with default remote repo in this case
        #(requires internet connection)
        print "Could not find destination path: %s" % remote_root

    for option in local_options:
        local_repo_path = os.path.join(local_root, option)
        remote_repo_path = os.path.join(remote_root, option)
        if os.path.exists(os.path.join(local_repo_path, '.hg')):
            sync_hg(hg_interface, local_repo_path, remote_repo_path)
        elif os.path.exists(os.path.join(local_repo_path, '.git')):
            sync_git(git_interface, local_repo_path, remote_repo_path)


        if ( os.path.exists(os.path.join(local_root, option, '.hg')) or
             os.path.exists(os.path.join(local_root, option, '.git')) ):
            if option in remote_options:
                print "'%s' is on remote media, preparing to sync..." % option
            else:
                #TODO:
                #could try syncronizing with default remote repo (via web) here
                print "%s is not on remote media, skipping" % option


def usage():
    print """
python /c/public/moments/moments/export.py /c/out/ /media/charles/CHARLES/out/
python /c/public/moments/moments/export.py /c/out/ /media/charles/WORK/out/
(reset any open journal buffers after export)

python /c/public/moments/moments/export.py /media/charles/WORK/out/ /c/out

/c/public/moments/mercurial_sync.py /c/clients /media/charles/WORK
/c/public/moments/mercurial_sync.py /media/charles/WORK/

/c/public/moments/mercurial_sync.py /c /media/CHARLES/

"""
        
if __name__ == '__main__':
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
            #NOT LOGICAL... SHOULDN'T EVER BE HERE
            #but it is nice to be more explicit with what the elif condition is
            exit()
    else:
        #go with the default here
        sync_repos()

    usage()
