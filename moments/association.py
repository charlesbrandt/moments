import re


#should also look at union and intersects for sets
# and tag.union

#maybe a function to:
# take a list of items
# take a list of itmes to ignore
# return a new list of items based on first, original, with ignores removed
# def filter_ignores(items, ignores):
def filter_list(items, ignores, search=False):
    for i in ignores:
        if i in items:
            items.remove(i)
        elif search:
            for item in items:
                if re.search(i, item):
                    items.remove(item)
        else:
            #must not match
            pass
    return items

def check_ignore(item, ignores=[]):
    """
    take a string (item)
    and see if any of the strings in ignores list are in the item
    if so ignore it.
    """
    ignore = False
    for i in ignores:
        if i and re.search(i, item):
            #print "ignoring item: %s for ignore: %s" % (item, i)
            ignore = True
    return ignore

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

    def items_by_frequency(self):
        keylist = self.frequency_list()
        keylist.sort()
        keylist.reverse()
        dlist = []
        for key in keylist:
            print "%s instances of %s" % (key[0], key[1])
            #represent ourself (dictionary) as a list of lists where:
            # [ [key, [items]], ... ]
            dlist.append([key[1], self[key[1]]])

        return dlist
    
    def max_key(self, ignores=[]):
        print ignores
        maxcount = 1
        maxkey = ''
        for key in self.keys():
            ignore = check_ignore(key, ignores)
            if not ignore:
                count = len(self[key])
                if count >= maxcount:
                    maxkey = key
                    maxcount = count
        return maxkey

    def min_key(self):
        ## mincount = maxcount
        ## for key in self.keys():
        ##     count = len(self[key])
        ##     mincount = min(count, mincount)

        mincount = None
        minkey = ''
        for key in self.keys():
            count = len(self[key])
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
        maxcount = len(self[maxkey])
        minkey = self.min_key()
        mincount = len(self[minkey])
        distribution = ( maxcount - mincount ) / 6
        keys = self.keys()
        keys.sort()
        for key in keys:
            if not check_ignore(key, ignores):
                if ( len(self[key]) == maxcount ):
                    size = "largestTag"
                elif len(self[key]) > ( mincount + (distribution*5) ):
                    size = "largerTag"
                elif len(self[key]) > ( mincount + (distribution*4) ):
                    size = "largeTag"
                elif len(self[key]) > ( mincount + (distribution*3) ):
                    size = "mediumTag"
                elif len(self[key]) > ( mincount + (distribution*2) ):
                    size = "smallTag"
                elif len(self[key]) > ( mincount + (distribution) ):
                    size = "smallerTag"
                elif len(self[key]) > mincount:
                    size = "tinyTag"
                elif len(self[key]) == mincount:
                    size = "tiniestTag"
                    
                url = url_template % key
                cloud += "<a href='%s' class='%s' alt='There are %s entries tagged as %s'>%s</a>\n" % ( url, size, str(len(self[key])), key, key )
        return cloud

    def make_log_cloud(self, steps):
        """
        http://www.car-chase.net/2007/jan/16/log-based-tag-clouds-python/
        """
        input = []
        for key in self.keys():
            input.append( (key, len(self[key])) )
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
