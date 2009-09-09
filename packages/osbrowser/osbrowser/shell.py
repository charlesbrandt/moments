#!/usr/bin/env python
from node import Directory

def ls(path):
    """
    create a Directory object
    and perform the equivalent command line action
    """
    result = ''
    d = Directory(path)
    d.contents.sort()
    for i in d.contents:
        result += i + '\n'
    print result
    return result

def du(path):
    """
    create a Directory object
    and perform the equivalent command line action
    """
    pass

def find(path):
    """
    create a Directory object
    and perform the equivalent command line action
    """
    pass

def grep(path):
    """
    create a Directory object
    and perform the equivalent command line action
    """
    pass

class Computer:
    """
    any information relevant to the current system 
    """
    pass

class Volume:
    """
    information about the drive/media that contains the files and directories 
    """
    pass

class URL:
    """
    might be nice to abstract similar properties of URLs and Nodes
    URLs could exist on local filesystem, but don't have to

    Nodes must be on the local system

    but both have a path, and potentially a title? (name?)
    """
    pass


