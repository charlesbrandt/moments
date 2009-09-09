import re, os

def split_path(path):
    """
    return a list of all parts of the path
    (os.path.split only splits into two parts, this does all)
    """
    parts = []
    #make sure the path we were sent starts with a slash for end case
    if not re.match('^\/', path):
        path = os.path.join('/', path)
        #print "new: %s" % path
    while path and path != '/':
        (path, suffix) = os.path.split(path)
        parts.insert(0, suffix)
    #print parts
    return parts

def path_to_tags(path):
    """
    looks at the specified path to generate a list of tags
    based on the file name and location

    check if the last item in the path is a file with an extension
    get rid of the extension if so
    """

    all_tags = Tags()
    path_parts = split_path(path)

    #get rid of filename extension
    last_part = path_parts[-1]
    last_part_name, last_part_extension = os.path.splitext(last_part)
    path_parts[-1] = last_part_name
    
    #convert each item to tags individually
    #each item in a path could be made up of multiple tags
    #i.e work-todo
    for p in path_parts:
        if p:
            part_tags = Tags().from_tag_string(p)
            for tag in part_tags:
                if tag not in all_tags:
                    all_tags.append(tag)

    return all_tags

def to_tag(item):
    """
    take any string and convert it to an acceptable tag

    tags should not contain spaces or special characters
    numbers, lowercase letters only
    underscores can be used, but they will be converted to spaces in some cases
    """
    item = item.lower()
    item = re.sub(' ', '_', item)
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

