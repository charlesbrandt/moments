"""
An entry is the foundation for a moment.  It does not require a date.

An entry can have more parts, but its most simple form is:
::

  * tags
  data
  \\n

should either data or a tag should be required?
(otherwise no way to tie it in... although a tag could be implied by location)

"""

import re
from tags import Tags

class Entry(object):
    """
    Object to hold a unique Journal Entry
    """
    def __init__(self, data=u'', tags=[], path=u''):
        self.data = data        
        self.tags = Tags(tags)
        #could rename this to path potentially
        #self.source_file = None
        self.path = path

    def tag_links(self):
        """
        return a list of tuples for each tag's association with all other tags
        """
        links = []
        if len(self.tags) > 1:
            for i in range(len(self.tags)-1):
                for j in range(i+1, len(self.tags)):
                    if self.tags[i] != self.tags[j]:
                        tmplist = [self.tags[i], self.tags[i+1]]
                        tmplist.sort()
                        link = tuple(tmplist)
                        if not link in links:
                            links.append(link)

        return links

    def omit_tags(self, tags):
        """
        remove tags from current set of tags if they exist
        
        scan entries.tags for each omit_tag
        remove it if found
        """
        if tags:
            for omit_tag in tags:
                if omit_tag in self.tags:
                    self.tags.remove(omit_tag)

    def change_newlines(self):
        """
        go through and convert all \\r\\n to \\n
        """
        filtered_data = ''
        for line in self.data.splitlines():
            #[ line ] = multi_filter( [line], updates)
            #[ line ] = multi_filter( [line], path_updates)
            filtered_data += line + '\n'

        self.data = filtered_data

    def render_first_line(self, format='text'):
        """
        return a textual representation of the first line only
        """
        line = ''
        if format == 'text':
            line = '* ' + ' '.join(self.tags) + "\n"
        elif format == 'html':
            line = u'<div class="entry_header"><span class="asterisk">*</span><span class="tags">%s</span></div>' % (' '.join(self.tags))
        return unicode(line)

    def render_data(self, format='text'):
        """
        return a textual representation of the entry data only
        """
        if self.data:
            #make sure that data is buffered with a blank line at the end
            #makes the resulting log easier to read.
            #if there are more than one blanklines, can leave them
            last_line = self.data.splitlines()[-1]
            #not re.match('\s', last_line) and
            
            #are there characters in the last line?  need to adjust if so:
            if re.search('\S', last_line):
                if re.search('\n$', last_line):
                    self.data += "\n"
                else:
                    #self.data += "\n"
                    #web entries added will end up with 3 newlines somehow
                    #but other entries created with a single string
                    #won't have enough new lines...
                    #should troubleshoot web entries
                    self.data += "\n\n"
            if format == 'text':
                return unicode(self.data)
            elif format == 'html':
                data = u''
                link_block = False
                for line in self.data.split('\n'):

                    #\s matches whitespace
                    #\S matches alphanumeric
                    #
                    #if it has characters, make it a 'line block'
                    #http://docutils.sourceforge.net/docs/user/rst/quickref.html
                    #if re.search('\S', line) and not re.match('^\s', line):
                    if re.search('^http:', line):
                        link_block = True
                    elif not re.search('\S', line):
                        #found a blank line, must have reached the end of any block
                        link_block = False

                    if link_block:
                        data += u"| " + line + u'\n'
                    else:
                        data += line + u'\n'

                        
                #to run through rest filter first:
                from docutils import core
                overrides = {'input_encoding': 'unicode',
                             'doctitle_xform': 1,
                             'initial_header_level': 1}
                parts = core.publish_parts(
                    source=data,
                    writer_name='html', settings_overrides=overrides)
                #fragment = parts['html_body']
                fragment = parts['fragment']
                #fragment = fragment.replace('\n', '<br>\n')
                fragment += '<p>&nbsp;</p>'
                return u'<div class="data">%s</div>' % fragment
            
                #no rest:
                #return u'<div class="data">%s</div>' % self.data
        else:
            #print "no data in this entry! : %s" % self.render_first_line()
            return ''

    def render(self, format='text', include_path=False):
        """
        return a textual representation of the entry

        include_path assumed to be false in some places
        """
        entry = u''
        entry += self.render_first_line(format)

        #in most cases we do not want to show the source path,
        #(it can change easily and frequently, and is determined on read)
        #but when merging and reviewing (summarize)
        #it could be useful to see in a temporary file
        if include_path:
            entry += self.path + "\n"
            
        entry += self.render_data(format)
        return entry

