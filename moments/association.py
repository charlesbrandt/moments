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

import re

#should also look at union and intersects for sets
# and tag.union

class Association(dict):
    """
    Object to hold dict of tags as keys, and the list of times as items
    """

    def key_has_item(self, key, item):
        """
        look at only one association

        will not fail if key does not exist.
        """
        if self.has_key(key) and item in self[key]:
            return True
        else:
            return False

    def keys_with_item(self, item):
        """
        return a list of keys that have that item
        """
        matches = []
        for k in self.keys():
            if self.key_has_item(k, item):
                matches.append(k)

        return matches
            
    def associate(self, item, key):
        if self.has_key(key):
            if not item in self[key]:
                self[key].append(item)
                #self[key].sort()
        else:
            self[key] = [ item ]


    def remove_association(self, item, key):
        #text_time = str(item.created)
        #text_time = item.created.strftime(time_format)
        if self.key_has_item(key, item):
            #text_time = time_to_text(item.created)
            self[key].remove(item)

    def remove(self, item):
        """
        remove all instances of item from all associations
        """
        for k in self.keys():
            self.remove_association(item, k)

    def frequency_list(self):
        """
        make a list of all unique items
        and how many times that item shows up in the journal

        return a list of tuples:
        [ (freq, item), ... ]
        """
        items = []
        for key in self.keys():
            items.append( (len(self[key]), key) )
        return items

    def frequent_first(self):
        """
        return a list of the keys... most frequent first
        """
        keylist = self.frequency_list()
        keylist.sort()
        keylist.reverse()
        dlist = []
        for key in keylist:
            dlist.append(key[1])
        return dlist

    def items_by_frequency(self):
        keylist = self.frequency_list()
        keylist.sort()
        keylist.reverse()
        dlist = []
        for key in keylist:
            #print "%s instances of %s" % (key[0], key[1])
            #represent ourself (dictionary) as a list of lists where:
            # [ [key, [items]], ... ]
            dlist.append([key[1], self[key[1]]])

        return dlist
    
