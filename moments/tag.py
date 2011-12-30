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
import re, os

def to_tag(item):
    """
    take any string and convert it to an acceptable tag

    tags should not contain spaces or special characters
    numbers, lowercase letters only
    underscores can be used, but they will be converted to spaces in some cases
    """
    item = item.lower()
    item = re.sub(' ', '_', item)
    item = re.sub("/", '_', item)
    item = re.sub("\\\\'", '', item)
    item = re.sub("\\'", '', item)
    item = re.sub("'", '', item)
    
    #todo:
    # filter any non alphanumeric characters
    
    return item

class Tags(list):
    """
    tags are typically just stored as a list of strings
    strings can have alphanumeric characters in them and the underscore ('_')

    individual tags should not have spaces

    this class collects methods
    to help convert to and from
    different formats of expressing tag collections
    """
    def __init__(self, tags=[]):
        #self = []
        list.__init__(self)
        self.extend(tags)
        
    def __str__(self):
        """
        returns just a space separated list of tags
        same format used in an moment log entry
        """
        return ' '.join(self)

    def from_spaced_string(self, tag_string):
        self.extend(tag_string.split(' '))
        return self

    def to_tag_string(self):
        """
        take a list of tags, and return the corresponding tag string
        tag1-tag2
        """
        return '-'.join(self)
        
    def from_tag_string(self, tag_string):
        """
        a tag string is a string of tags separated by a '-'
        easy to split with python,
        but for a consistent interface
        using this
        """
        #self = tag_string.split('-')
        self.extend(tag_string.split('-'))
        return self
    
    def union(self, tag_list):
        """
        take the list of tags supplied
        and add any tags that we don't have
        """
        for t in tag_list:
            if t not in self:
                self.append(t)

    def is_equal(self, other):
        equal = True
        for t in other:
            if t not in self:
                equal = False
        return equal
                
    def omit(self, tags=[]):
        """
        remove tags from current set of tags if they exist
        """
        for omit_tag in tags:
            if omit_tag in self:
                self.remove(omit_tag)



def from_tag(item):
    """
    ***doesn't work well in practice***

    take any tag and attempt to make it more human readable

    should just keep them as tags usually
    
    """
    item = re.sub('_', ' ', item)
    parts = item.split(' ')
    new_parts = []
    for p in parts:
        new_parts.append(p.capitalize())
    item = ' '.join(new_parts)
    return item

