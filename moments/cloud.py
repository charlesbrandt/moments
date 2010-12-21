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

"""

class Cloud(object):
    def __init__(self, dictionary=None):
        self.dict = dictionary

    def max_key(self, ignores=[]):
        """
        find the key with the largest number of values
        """
        #print ignores
        maxcount = 1
        maxkey = ''
        for key in self.dict.keys():
            ignore = check_ignore(key, ignores)
            if not ignore:
                count = len(self.dict[key])
                if count >= maxcount:
                    maxkey = key
                    maxcount = count
        return maxkey

    def min_key(self):
        """
        find the key with the smallest number of values
        """
        ## mincount = maxcount
        ## for key in self.dict.keys():
        ##     count = len(self.dict[key])
        ##     mincount = min(count, mincount)

        mincount = None
        minkey = ''
        for key in self.dict.keys():
            count = len(self.dict[key])
            if not minkey or count < mincount:
                minkey = key
                mincount = count
        return minkey

    def make_cloud(self, url_template='%s', ignores=[]):
        """
        take an association, create a cloud of the keys in the association
        based on the number of items associated with each key

        inspired by:
        timfanelli.com/projects/tag_cloud.txt

        url_template should have one string substitution for where the tag goes
        """
        cloud = ''
        maxkey = self.max_key(ignores)
        maxcount = len(self.dict[maxkey])
        minkey = self.min_key()
        mincount = len(self.dict[minkey])
        distribution = ( maxcount - mincount ) / 6
        keys = self.dict.keys()
        keys.sort()
        for key in keys:
            if not check_ignore(key, ignores):
                if ( len(self.dict[key]) == maxcount ):
                    size = "largestTag"
                elif len(self.dict[key]) > ( mincount + (distribution*5) ):
                    size = "largerTag"
                elif len(self.dict[key]) > ( mincount + (distribution*4) ):
                    size = "largeTag"
                elif len(self.dict[key]) > ( mincount + (distribution*3) ):
                    size = "mediumTag"
                elif len(self.dict[key]) > ( mincount + (distribution*2) ):
                    size = "smallTag"
                elif len(self.dict[key]) > ( mincount + (distribution) ):
                    size = "smallerTag"
                elif len(self.dict[key]) > mincount:
                    size = "tinyTag"
                elif len(self.dict[key]) == mincount:
                    size = "tiniestTag"
                    
                url = url_template % key
                cloud += "<a href='%s' class='%s' alt='There are %s entries tagged as %s'>%s</a>\n" % ( url, size, str(len(self.dict[key])), key, key )
        return cloud

    def make_log_cloud(self, steps):
        """
        http://www.car-chase.net/2007/jan/16/log-based-tag-clouds-python/
        """
        input = []
        for key in self.dict.keys():
            input.append( (key, len(self.dict[key])) )
            if not type(input) == types.ListType or len(input) <= 0 or steps <= 0:  
                raise InvalidInputException, "Please be sure steps > 0 and your input list is not empty."  
            else:  
                temp, newThresholds, results = [], [], []  
                for item in input:  
                    if not type(item) == types.TupleType:  
                        raise InvalidInputException, "Be sure input list holds tuples."  
                    else:
                        temp.append(item[1])  
        Weight = float(max(temp))  
        minWeight = float(min(temp))  
        newDelta = (maxWeight - minWeight)/float(steps)  
        for i in range(steps + 1):  
            newThresholds.append((100 * math.log((minWeight + i * newDelta) + 2), i))  
            for tag in input:  
                fontSet = False  
                for threshold in newThresholds[1:int(steps)+1]:  
                    if (100 * math.log(tag[1] + 2)) <= threshold[0] and not fontSet:  
                        results.append(dict({str(tag[0]):str(threshold[1])}))  
                        fontSet = True  
        return results  
