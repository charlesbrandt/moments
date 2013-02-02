#from xml.etree.ElementTree import ElementTree
#tree = ElementTree()
#this reads in the xml data from a file:
#tree.parse("evernote_export-20110809.enex")

from xml.etree import ElementTree

from moments.journal import Journal
from moments.moment import Moment
from moments.timestamp import Timestamp
f = open("evernote_export-20110809.enex")
root = ElementTree.fromstring(f.read())
print root
#<Element 'html' at 0xb77e6fac>

journal = Journal()

cur_moment = None
for element in root.getiterator():
    if element.tag == "note":
        if cur_moment:
            journal.update(cur_moment)
        cur_moment = Moment()
    elif element.tag == "tag":
        cur_moment.tags.append(element.text)
    elif element.tag == "created":
        ts = Timestamp()
        ts.from_apple_compact(element.text)
        cur_moment.created = ts
    elif element.tag == "title":
        cur_moment.data = element.text + "\n\n" + cur_moment.data
    elif element.tag == "content":
        #TODO:
        #convert to text from xml
        cur_moment.data = cur_moment.data + element.text

journal.save("temp.txt")
#print element
#print dir(element)
#print element.text
#print element.tag


#p = tree.find("en-note")     # Finds first occurrence of tag p in body
#entries = list(tree.iter("en-note"))
#for e in tree.items():
#    print e
