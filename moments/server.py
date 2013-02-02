#!/usr/bin/env python
"""
# By: Charles Brandt [code at contextiskey dot com]
# On: 2011.06.09 15:41:45 
# License:  MIT 

# Requires:
# bottle.py

# Description:

aka JournalServer
this should only serve a journal item
using as close of an API as a journal itself
and only returning json objects

mimicing Mindstream, but incorporating bottle
for json only server

some other similarities with pose application

*2011.07.13 07:22:44
this is a handy way to test different commands, since firefox will not display json by default (prompts to save it):
wget -q -O - http://localhost:8000/entries

*2011.08.18 14:44:22
(port argument can be anywhere)
python server.py /c/journal/ -p 8001 /c/charles

python server.py /c/journal/ /c/charles
"""
import sys, os, re

from path import load_journal as load_journal_path
from journal import Journal
from moment import Moment
from timestamp import Timestamp

#bottle will handle returning dicts as json automatically
#sometimes it is nice to simply return a list as json
try:
    import simplejson as json
except:
    try:
        import json
    except:
        print "No json module found"
        exit()
                
#from bottle import static_file
#from bottle import get, post, request
#from bottle import route
#from bottle import template
from bottle import run, request

import bottle

debug = True
if debug:
    #DO NOT USE THIS IN PRODUCTION!!
    bottle.debug(True)

server = bottle.Bottle()

#where we store what we've loaded
j = Journal()

path_root = '/c/outgoing/'

@server.route('/save/:item#.+#')
def save(item):
    global j, path_root
    full_path = os.path.join(path_root, item)
    number = j.save(full_path)
    return "%s saved (%s entries) (full path: %s)" % (item, number, full_path)

@server.post('/save/')
@server.post('/save')
def save_post():
    global j
    destination = request.forms.get('destination')
    full_path = os.path.join(path_root, destination)
    number = j.save(full_path)
    return "%s saved (%s entries) (full path: %s)" % (item, number, full_path)

@server.route('/load_journal/:item#.+#')
def load_journal(item):
    """
    if we load root automatically on start,
    this won't have much use if we limit loads to the root directory
    (as we do in normal load() and load_post())
    but if we don't, that could have some security implications
    (loading anywhere in the filesystem)
    may or may not want to enable, depending on the environment in use
    """
    global j
    temp_j = load_journal_path(item)
    entries = temp_j.entries()
    j.update_many(entries)
    return "%s loaded (%s entries)" % (item, len(entries))

@server.route('/load/:item#.+#')
def load(item):
    global j, path_root
    full_path = os.path.join(path_root, item)
    number = j.load(full_path)
    return "%s loaded (%s entries) (full path: %s)" % (item, number, full_path)

@server.post('/load/')
@server.post('/load')
def load_post():
    global j
    source = request.forms.get('source')
    j.load(source)
    
@server.route('/reload')
def reload():
    """
    """
    global j
    j.reload()

def validate(data, tags, created):
    tags = tags.split(' ')

    if re.search('\.', created):
        ts = Timestamp(created)
    else:
        ts = Timestamp(compact=created)

    return [data, tags, ts]

@server.get('/make')
def make_form():
    return """<form method="POST">
                 created: <input name="created" type="datetime" />
                 tags: <input name="tags" type="text" />
                 data: <input name="data" type="text" />
                 source: <input name="source" type="text" />
                 position: <input name="position" type="text" />
                 <button name="submit" value="Make" type="submit">Make</button>
              </form>"""

@server.post('/make')
def make():
    global j
    created = request.forms.get('created')
    tags = request.forms.get('tags')
    data = request.forms.get('data')
    source = request.forms.get('source')
    position = request.forms.get('position')
    position = int(position)
    
    #convert & verify data recieved as needed here
    data, tags, ts = validate(data, tags, created)
    
    entry = j.make(data, tags, ts, source, position)
    return entry.as_dict()
    
def _lookup(data, tags, created):
    """
    return the Moment containing matching content passed in

    *2011.07.09 10:46:16 
    abstract "check for existing" functionality in journal.update
    may be other cases it is useful
    as in a lookup entry on the journal server, before remove
    to make sure we get the equivalent moment (not creating a copy)

    similar to journal.date()

    I think the right answer is to make an entry
    use journal.date() to get any other entries at that time
    then for each entry (even if just one)
    check if the entry is_equal
    if so, remove

    """
    global j
    moment = Moment(data=data, created=created, tags=tags)
    options = j.date(created)
    if len(options):
        matches = []
        for o in options:
            print "type moment: %s, type o: %s" % (type(moment), type(o))
            if moment.is_equal(o):
                matches.append(o)
                
        #we should only have one item at most if there was a match
        assert len(matches) <= 1
        if len(matches):
            return matches[0]
        else:
            return None
    else:
        #no existing option
        return None
    
@server.get('/remove')
def remove_form():
    return """<form method="POST">
                 date: <input name="created" type="datetime" />
                 tags: <input name="tags" type="text" />
                 data: <input name="data" type="text" />
                 <button name="submit" value="Remove" type="submit">Remove</button>
              </form>"""

@server.post('/remove')
def remove():
    global js
    created = request.forms.get('created')
    tags = request.forms.get('tags')
    data = request.forms.get('data')

    #convert & verify data recieved as needed here
    data, tags, ts = validate(data, tags, created)

    match = _lookup(data, tags, ts.compact())
    if match:
        j.remove(match)
        return "True"
    else:
        return "False"

    
@server.route('/tag/:name')
@server.route('/tag/:name/')
def tag(name):
    global j
    entries = j.tag(name)
    #print "TAGS: %s" % entries
    d = {name:[]}
    for e in entries:
        d[name].append(e.as_dict())
    return d

@server.route('/tags')
@server.route('/tags/')
def tags():
    global j
    return j.tags()

@server.route('/date/:compact')
@server.route('/date/:compact/')
def date(compact):
    global j
    entries = j.date(compact)

    d = {}
    #print "SERVER entries: %s" % entries
    #for key in entries.keys():
    #print "key: %s" % key
    d[compact] = []
    for e in entries:
        #print e
        d[compact].append(e.as_dict())
        
    return d

@server.route('/dates')
@server.route('/dates/')
def dates():
    """
    """
    global j
    return j.dates()

@server.route('/entry/:index')
@server.route('/entry/:index/')
def entry(index):
    global j
    entry = j.entry(int(index))
    if entry:
        return entry.as_dict()
    else:
        return {}

@server.route('/entries')
@server.route('/entries/')
def entries():
    """
    """
    global j
    entries = j.entries()
    d = {'entries':[]}
    for e in entries:
        d['entries'].append(e.as_dict())
    return d
    
    #return j.entries()

@server.route('/related/:name')
@server.route('/related/:name/')
def related(name):
    global j
    related_list = j.related(name)
    return { name : related_list }

@server.route('/search/data/:key')
@server.route('/search/data/:key/')
def search_data(key):
    global j
    entries = j.search(key, data=True)
    results = []
    for e in entries:
        results.append(e.as_dict())
    return { 'matches' : results }


@server.route('/search/:key/:limit/')
@server.route('/search/:key/:limit')
@server.route('/search/:key/')
@server.route('/search/:key')
@server.route('/search/')
@server.route('/search')
def search(key=None, limit=20):
    global j
    if key is None:
        key = request.GET.get('term')

    #print key
    tags = j.search(key, limit=limit)
    #return { 'matches' : tags }
    return json.dumps(tags)

## @server.route('/search/:key')
## @server.route('/search/:key/')
## def search(key):
##     global j
##     tags = j.search(key)
##     return { 'matches' : tags }

@server.route('/sort/:order')
@server.route('/sort/:order/')
def sort(order):
    global j
    entries = j.sort(order)
    results = []
    for e in entries:
        results.append(e.as_dict())
    return { 'entries' : results }

@server.route('/range/:start/:end/')
@server.route('/range/:start/:end')
@server.route('/range/:start/')
@server.route('/range/:start')
@server.route('/range/')
@server.route('/range')
def range(start=None, end=None):
    global j
    if start:
        entries = j.range(start, end)
        results = []
        for e in entries:
            results.append(e.as_dict())
        return { 'entries' : results }
    else:
        return str(j.range())

@server.route('/clear')
@server.route('/clear/')
@server.route('/clear/mind')
@server.route('/clear/mind/')
def clear():
    global j
    result = j.clear()
    return "Clear as a mountain stream.<br>(result: %s)" % result

def usage():
    print __doc__    

if __name__ == '__main__':
    source = None
    port = 8000
    found_root = None
    if len(sys.argv) > 1:
        helps = ['--help', 'help', '-h']
        for i in helps:
            if i in sys.argv:
                usage()
                exit()

        ports = ['--port', '-p']
        for p in ports:
            if p in sys.argv:
                i = sys.argv.index(p)
                sys.argv.pop(i)
                port = sys.argv.pop(i)

        proots = ['--root', '-r', '-c', '--context']
        for p in proots:
            if p in sys.argv:
                i = sys.argv.index(p)
                sys.argv.pop(i)
                path_root = sys.argv.pop(i)
                found_root = path_root

        #if len(sys.argv) > 2:
        #    port = sys.argv[2]

        sources = sys.argv[1:]
        for s in sources:
            #this will get the first one to use as primary path_root
            if not source:
                source = s
                
            load_journal(s)
            print "Loaded: %s entries" % len(j.entries())
            
    if source and not found_root:
        path_root = source
    else:
        #look_in('/c/outgoing')
        pass

    #load_journal(path_root)

    #bottle.Bottle.mount(server)
    run(app=server, host='localhost', port=port)
