*2008.11.02 08:27 
4 files in this directory:

************************
convert_itunes_to_m3u.py  (imports ElementPList.py)
************************
actual usage:
mkdir m3us
python convert_itunes_to_m3u.py --input "/home/charles/charles/media/binaries/music-other/itunes_library_backups/20081027-powerbook-charles_account/iTunes Music Library.xml" --output m3us

# With usage like the following:  (assuming filename of iTunesExport)
#
#>>> from iTunesExport import exportPlaylists
#>>> BASE = "/Volumes/itunes/__Playlists__"
#>>> exportPlaylists('%s/Library.xml' % BASE, BASE)

convert_itunes_xml.py
#2008.08.25 13:22
# this was an initial custom attempt to decode itunes playlist (plist) xml files
# subsequently found convert_itunes_to_m3u which utilizes ElementPList

itunes2m3u.py
# 2008.08.25 13:28
# initial tests some time ago didn't seem to work with this script
# see convert_itunes_to_m3u.py






*2008.08.27 21:07 itunes import export
export and merge playlists
must extract playlists from itunes some how

this is essentially finished
there may be others,
but for now there is enough to work on sorting through older playlists
to generate statistics
also [2008.04.22 18:56] 
export iTunes playlists
#2008.08.26 21:32 
trying this again
wasn't ready the last time it happened
#2008.07.25 05:56 
starting a new itunes instance
this one should import all music locally
#2008.07.25 04:54 
create a new itunes library
copy all music from a playlist into library
#2008.04.22 18:56 
export iTunes playlists
also [2008.02.20 20:01:24] music@one:/Volumes/music/playlists/charles/itunes
python ~/meta/code/python/itunes_conversion/itunes2m3u.py 20080216-landlocked.xml
Parsing 20080216-landlocked.xml... done
20080216-landlocked.m3u: 66 tracks
also [2008.02.20 19:56]
python ~/meta/code/python/itunes_conversion/itunes2m3u.py
also [2008.02.20 10:33]
import music from landlocked 20080216
also [2008.02.18 01:03]
run convert_itunes_to_m3u on macbook and powerbook.
sort through playlists in:
MUSIC:playlists:charles.
*2008.02.17 21:54 harvest playlists
export expedition listen, and any others from tessa powerbook in living room
vnc there.
requested [2008.02.17 21:49] playlists
after images have been imported, digitized, etc, parsed (OCR)
synchronize phone
synchronize playlists
look at recently played.
might need multiple copies for one day
make as many playlists as needed for a specific day, as long as playlists start with a specific date first (not tag first)  (only one per tag-date) (i.e. tag is listed as more important for that day.)
also [2008.02.17 17:09]
export playlist from itunes to:
MUSIC:playlists:charles:itunes:date
open DD


*2008.02.18 18:18 
finally found an itunes library to m3u converter that worked

*2008.02.18 11:44 
get music to come out of deckadance
export playlists
convert one to m3u... somehow!!

*2008.02.18 02:30 python elementtree music itunes_conversion
tried three different versions of element tree, all gave the same problems

I'm guessing at this point that something within the iTunes XML format changed.
bah
bed time

*2008.02.18 02:25 14 music@one:~/meta/code/python/playlists
python ../convert_itunes_to_m3u.py --input "iTunes Music Library.xml"
Description from header would be cool here
INPUT: iTunes Music Library.xml
Traceback (most recent call last):
  File "../convert_itunes_to_m3u.py", line 139, in ?
    main()
  File "../convert_itunes_to_m3u.py", line 135, in main
    pls. exportPlaylists()
  File "../convert_itunes_to_m3u.py", line 96, in exportPlaylists
    for playlist in self.lib['Playlists']:
TypeError: unsubscriptable object

*2008.02.18 01:54 end
*2008.02.18 01:53 37 music@one:~/meta/code/python/playlists
python2.5 ../convert_itunes_to_m3u.py --input "iTunes Music Library.xml"
Traceback (most recent call last):
  File "../convert_itunes_to_m3u.py", line 27, in <module>
    from ElementPList import load
ImportError: No module named ElementPList

*2008.02.17 23:17 
export playlists from mac book too
if not "exported" folder exists in ituness:
   make exported folder

export a playlist in itunes
import that playlist in deckadance

*2008.02.15 22:16 music library migration
completed:

*2008.02.15 22:14 end
*2008.02.15 22:15 39 music@one:~/Music/iTunes
sudo mv /Users/charles/Music/iTunes/iTunes\ Music\ Library.xml .
sudo chown -R music: *

*2008.02.15 22:16 end
*2008.02.15 22:14 18 music@one:~/Music/iTunes
sudo mv /Users/charles/Music/iTunes/iTunes\ Library .
Password:

*2008.03.16 00:50 
review steps to export an itunes playlist to m3u for use in deckadance

