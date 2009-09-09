from journal import Journal
from gvgen import *
import os

class Graph:
    #place to store the number of unique links that a given tag has
    #(write those first?)
    tag_list = {}

    #a simple list of all of the link tuples
    links = []

    name = None
    j = None

    def __init__(self, name, journal):
        self.name = name
        self.j = journal

    def make_links(self):
        #look at each entry
        for e in self.j.entries.values():
            #get the links for the current entry:
            elinks = e.tag_links()
            for link in elinks:
                if not link in self.links:
                    self.links.append(link)
                for t in link:
                    if self.tag_list.has_key(t):
                        self.tag_list[t] += 1
                    else:
                        self.tag_list[t] = 1

    def tags_in_order(self):
        items = self.tag_list.items()
        items = [(v, k) for (k, v) in items]
        items.sort()
        items.reverse()         # so largest is first
        items = [k for (v, k) in items]

        return items
        #links = link_list.keys()

    def write_graph(self):
        tags = self.tags_in_order()

        items = {}
        graph = GvGen()

        for tag in tags:
            items[tag] = graph.newItem(tag)

        for link in self.links:
            graph.newLink(items[link[0]], items[link[1]])

        fname = self.name + '.dot'
        f = open(fname, 'w')
        graph.dot(f)
        f.close()

    def write_graph2(self):
        tags = self.tags_in_order()

        items = {}
        graph = GvGen()

        for tag in tags:
            items[tag] = graph.newItem(tag)

        for tag in tags:
            for link in self.links:
                if tag in link:
                    self.links.remove(link)
                    tlink = list(link)
                    tlink.remove(tag)
                    other_tag = tlink[0]
                    graph.newLink(items[tag], items[other_tag])

        fname = self.name + '.dot'
        f = open(fname, 'w')
        graph.dot(f)
        f.close()


def graph_orig(ifile):
    """
    this was the original attempt at generating .dot graph files
    it works for the most part, though graphviz says 'failed to render'
    (but still renders)

    does not use directed links like gvgen
    keeping around just in case

    #place for dot graph definition
    """
    #make graph filename from ifile
    (path, name) = os.path.split(ifile)
    (fname, suffix) = name.split('.')

    j = Journal()
    j.add_file(ifile)
    #place to store tuples of (tag, tag) and the entries that give those links:
    link_list = {}

    #place to store the number of unique links that a given tag has
    #(write those first?)
    tag_list = {}

    #look at all tags in journal
    for tname in j.tags.keys():

        #look at each entry associated with a tag
        for etime in j.tags[tname].entry_times:
            e = j.entries[etime]

            #look at the tags associated with an entry to make a tag link
            for etag in e.tags:
                if etag != tname:
                    tmplist = [etag, tname]
                    tmplist.sort()
                    link = tuple(tmplist)
                    if link_list.has_key(link):
                        link_list[link].append(etime)
                    else:
                        link_list[link] = [ etime ]
                        #we have a new unique link, we'll update the tag_list
                        if tag_list.has_key(tname):
                            tag_list[tname] += 1
                        else:
                            tag_list[tname] = 1


    items = tag_list.items()
    items = [(v, k) for (k, v) in items]
    items.sort()
    items.reverse()         # so largest is first
    items = [(k, v) for (v, k) in items]

    links = link_list.keys()


    f = open(fname + '.dot', 'w')
    f.write('graph Map {')
    f.write('node [shape=ellipse];')
    for tname in j.tags.keys():
        f.write(tname + '; ')
    f.write('\n\n')

    for (tag, v) in items:
        for link in links:
            if tag in link:
                node1 = link[0]
                node2 = link[1]
                link_count = len(link_list[link])
                links.remove(link)
                #f.write('%s -- %s [label="%s",len=1.00];\n' % (node1, node2, link_count))
                f.write('%s -- %s;\n' % (node1, node2))

    f.write('label = "\n2007\n";\nfontsize=20;}')
    f.close()



