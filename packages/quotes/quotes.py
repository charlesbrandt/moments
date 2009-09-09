#!/usr/bin/env python
"""
#
# Description:
# Display a quote from the quote file passed to the Quote object initialization
# based on the position in position.txt
#
# By: Charles Brandt [code at contextiskey dot com]
# On: 2009.01.22
# Updated: 2009.03.25
# License: MIT

# Sources:
#
"""

import os, re
from medialist.medialist import MediaList

class Quotes:
    def __init__(self, filename=None):
        if not filename:
            filename = "sutras.txt"

        f = open(filename)
        self.filename = filename
        
        quotes = MediaList(loop=True)
        cur_quote = ''
        for line in f.readlines():
            if line == '\n':
                quotes.append(cur_quote)
                cur_quote = ''
            else:
                cur_quote += line

        f.close
        self.quotes = quotes

        self.pos_file = "position.txt"
        f = open(self.pos_file)
        cur_pos = f.readline()
        f.close()
        self.quotes.cur_pos = int(cur_pos.strip())
        
        #return quotes, cur_pos

    def lookup_quote(self, number):
        for s in self.quotes:
            if re.match(number, s):
                return s
        return None

    def to_html(self, s):
        s = s.replace('\n', '<br>\n')
        return s
    
    def next(self, format='html'):
        s = self.quotes.get_next()
        f = open(self.pos_file, 'w+')
        f.seek(0)
        f.write(str(self.quotes.cur_pos))
        f.close()
        if format == 'html':
            s = self.to_html(s)
        return s
