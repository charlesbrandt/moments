#2008.08.25 13:22
# this was an initial custom attempt to decode itunes playlist (plist) xml files
#
# subsequently found convert_itunes_to_m3u which utilizes ElementPList

import cElementTree as et
filename = '/Volumes/MUSIC/playlists/charles/itunes/expedition-20080217.xml'
tree = et.parse(filename)
root = tree.getroot()
template = '%s: %s'
for i in root.find('./*/dict').getchildren():
     if i.tag == 'dict':
         data = i.getchildren()
         for j in range(0,len(data)):
             if data[j].tag == 'key':
                 if data[j].text == 'Name':
                      print template % ('Song Name', data[j+1].text)
                 if data[j].text == 'Artist':
                      print template % ('Band Name', data[j+1].text)
                 if data[j].text == 'Total Time':
                      converted = '%s:%.2s' % divmod(int(data[j+1].text), 60000)
                      print template % ('Length', converted)


