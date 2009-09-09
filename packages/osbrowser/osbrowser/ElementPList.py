#*2008.02.18 02:05 requires:
# elementtree library
# http://effbot.org/zone/element-index.htm

# cElementTree is included with Python 2.5 and later, as xml.etree.cElementTree.

#*2008.11.11 13:10
#http://effbot.org/zone/element-iterparse.htm
# towards the end there is an example of iterparse in action, specifically for
# Apple plists

try:
    from xml.etree.cElementTree import iterparse
except ImportError:
    from xml.etree.ElementTree import iterparse

#try:
#    from cElementTree import iterparse
#except ImportError:
#    from elementtree.ElementTree import iterparse

import base64, datetime, re

unmarshallers = {

    # collections
    "array": lambda x: [v.text for v in x],
    "dict": lambda x:
        dict((x[i].text, x[i+1].text) for i in range(0, len(x), 2)),
    "key": lambda x: x.text or "",

    # simple types
    "string": lambda x: x.text or "",
    "data": lambda x: base64.decodestring(x.text or ""),
    "date": lambda x:
        datetime.datetime(*map(int, re.findall("\d+", x.text))),
    "true": lambda x: True,
    "false": lambda x: False,
    "real": lambda x: float(x.text),
    "integer": lambda x: int(x.text),

}

def load(file):
    parser = iterparse(file)
    for action, elem in parser:
        unmarshal = unmarshallers.get(elem.tag)
        if unmarshal:
            data = unmarshal(elem)
            elem.clear()
            elem.text = data
            #if elem.tag == "dict":
            #    print "Tag: %s, Data: %s" % (elem.tag, elem.text)
        elif elem.tag != "plist":
            raise IOError("unknown plist type: %r" % elem.tag)
    return parser.root[0].text
