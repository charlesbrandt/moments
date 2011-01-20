#!/usr/bin/python
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
# By: Charles Brandt <code at contextiskey dot com>
# On: *2010.12.20 16:56:09 
# License:  MIT

# Description:

separating out logic to represent a tag cloud from Association
will still use a journal (and it's associations) to generate the cloud.

*2011.01.13 15:58:19
converted to object
standard cloud seems better than logarithmic one... something not quite right with the math in logarithmic.
"""
import types, math
from path import check_ignore

class TagList(list):
    """
    *2011.01.13 19:08:58 
    a tag list is an ordered list of tags that are a subset of another group of
    tags

    might be able to just use Tags()

    this should be an ordered list
    of tags / topics of interest
    for a particular context

    that way it should be easier / possible to narrow down a tag cloud
    to just items of interest
    """
    pass

class Cloud(object):
    def __init__(self, source=None, steps=7, ignores=[]):
        #source is likely an Association
        #which is just a dictionary
        #where each key references a list of items
        
        #the length of that list is used to determine the size of the key
        self.source = source
        #and that info is stored in result
        #(as a list of tuples:
        #[ (tag, size), ... ]
        self.results = []

        #the number of sizes to assign for the cloud
        self.steps = steps

        self.debug = ''

        self.ignores = ignores

    def max_key(self):
        """
        find the key with the largest number of values
        """
        #print ignores
        maxcount = 1
        maxkey = ''
        for key in self.source.keys():
            ignore = check_ignore(key, self.ignores)
            if not ignore:
                count = len(self.source[key])
                if count >= maxcount:
                    maxkey = key
                    maxcount = count
        return maxkey

    def min_key(self):
        """
        find the key with the smallest number of values
        """
        ## mincount = maxcount
        ## for key in self.source.keys():
        ##     count = len(self.source[key])
        ##     mincount = min(count, mincount)

        mincount = None
        minkey = ''
        for key in self.source.keys():
            count = len(self.source[key])
            if not minkey or count < mincount:
                minkey = key
                mincount = count
        return minkey

    def render(self, url_template='%s'):
        #this should be the same length as steps 
        mappings = ["tiniestTag", "tinyTag", "smallerTag", "smallTag", "mediumTag", "largeTag", "largerTag", "largestTag"]

        cloud = ''
        #enable debug message:
        cloud += self.debug
        
        for item in self.results:
            #print item
            size = mappings[item[1]]
            key = item[0]
            url = url_template % key
            cloud += "<a href='%s' class='%s' alt='%s entries tagged %s'>%s</a>\n" % ( url, size, str(len(self.source[key])), key, key )
        return cloud
            
    def make(self):
        """
        take an association, create a cloud of the keys in the association
        based on the number of items associated with each key

        inspired by:
        timfanelli.com/projects/tag_cloud.txt

        url_template should have one string substitution for where the tag goes
        """
        cloud = ''
        maxkey = self.max_key()
        maxcount = len(self.source[maxkey])
        minkey = self.min_key()
        mincount = len(self.source[minkey])
        distribution = ( maxcount - mincount ) / self.steps
        #self.debug += "maxkey: %s, maxcount: %s, minkey: %s, mincount: %s, distribution: %s <br>\n" % (maxkey, maxcount, minkey, mincount, distribution)
        keys = self.source.keys()
        keys.sort()
        for key in keys:
            if not check_ignore(key, self.ignores):
                #self.debug += "looking at key: %s<br>\n" % key
                found = False
                for step in range(self.steps-1, -2, -1):
                    #self.debug += "checking step: %s<br>\n" % step
                    if len(self.source[key]) > ( mincount + (distribution*step) ):
                        self.results.append( (key, step+1) )
                        found = True
                        break

                if not found:
                    self.debug += "NOT FOUND. key len: %s" % len(self.source[key])

    def make_logarithmic(self):
        """
        http://www.car-chase.net/2007/jan/16/log-based-tag-clouds-python/
        """
        input = []
        keys = self.source.keys()
        keys.sort()
        for key in keys:
            input.append( (key, len(self.source[key])) )
            if not type(input) == types.ListType or len(input) <= 0 or self.steps <= 0:  
                raise InvalidInputException, "Please be sure steps > 0 and your input list is not empty."  
            else:  
                temp, newThresholds, results = [], [], []  
                for item in input:  
                    if not type(item) == types.TupleType:  
                        raise InvalidInputException, "Be sure input list holds tuples."  
                    else:
                        temp.append(item[1])  

        maxWeight = float(max(temp))  
        minWeight = float(min(temp))  
        newDelta = (maxWeight - minWeight)/float(self.steps)
        #self.debug += str(input)
        for i in range(self.steps + 1):  
            newThresholds.append((100 * math.log((minWeight + i * newDelta) + 2), i))  
        for tag in input:  
            if not check_ignore(tag[0], self.ignores):
                fontSet = False  
                for threshold in newThresholds[1:int(self.steps)+1]:  
                    if (100 * math.log(tag[1] + 2)) <= threshold[0] and not fontSet:  
                        #self.results.append(dict({str(tag[0]):str(threshold[1])}))  
                        self.results.append((str(tag[0]), threshold[1]))  
                        fontSet = True  
        return self.results  
