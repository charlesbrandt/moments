# $Id$
# -*- coding: latin-1 -*-
# use a dynamically populated translation dictionary to remove accents
# from a string
#
# http://effbot.python-hosting.com/file/stuff/sandbox/text/unaccent.py
# http://www.crummy.com/cgi-bin/msm/map.cgi/ASCII%2C+Dammit
# http://www.peterbe.com/plog/unicode-to-ascii
# see also phraseUnicode2ASCII()

import unicodedata, sys

CHAR_REPLACEMENT = {
    # latin-1 characters that don't have a unicode decomposition
    0xc6: u"AE", # LATIN CAPITAL LETTER AE
    0xd0: u"D",  # LATIN CAPITAL LETTER ETH
    0xd8: u"OE", # LATIN CAPITAL LETTER O WITH STROKE
    0xde: u"Th", # LATIN CAPITAL LETTER THORN
    0xdf: u"ss", # LATIN SMALL LETTER SHARP S
    0xe6: u"ae", # LATIN SMALL LETTER AE
    0xf0: u"d",  # LATIN SMALL LETTER ETH
    0xf8: u"oe", # LATIN SMALL LETTER O WITH STROKE
    0xfe: u"th", # LATIN SMALL LETTER THORN
    }

##
# Translation dictionary.  Translation entries are added to this
# dictionary as needed.

class unaccented_map(dict):
    ##
    # Maps a unicode character code (the key) to a replacement code
    # (either a character code or a unicode string).

    def mapchar(self, key):
        ch = self.get(key)
        if ch is not None:
            return ch
        de = unicodedata.decomposition(unichr(key))
        if de:
            try:
                ch = int(de.split(None, 1)[0], 16)
            except (IndexError, ValueError):
                ch = key
        else:
            ch = CHAR_REPLACEMENT.get(key, key)
        self[key] = ch
        return ch

    if sys.version >= "2.5":
        # use __missing__ where available
        __missing__ = mapchar
    else:
        # otherwise, use standard __getitem__ hook (this is slower,
        # since it's called for each character)
        __getitem__ = mapchar


def to_ascii(source):
    #print type(source)
    #source = source.translate(unaccented_map()).encode("ascii", "ignore")
    source = source.translate(unaccented_map())
    return source

def to_unicode(source):
    s = u''
    for c in source:
        try:
            s += unicode(c)
        except:
            pass
    return s

def to_ascii2(source):
    s = to_unicode(source)
    s = to_ascii(s)
    return s


if __name__ == "__main__":

    text = u"""

    "Jo, n�r'n da ha g�tt ett st�ck te, s� kommer'n te e �,
    � i �a � e �."
    "Vasa", sa'n.
    "� i �a � e �", sa ja.
    "Men va i all ti � d� ni s�jer, a, o?", sa'n.
    "D'� e �, vett ja", skrek ja, f�r ja ble rasen, "� i �a
    � e �, h�rer han lite, d'� e �, � i �a � e �."
    "A, o, �", sa'n � d�mm� geck'en.
    Jo, den va n�e te dum den.

    (taken from the short story "Dumt f�lk" in Gustaf Fr�ding's
    "R�ggler � paschaser p� v�ra m�l t� en bonne" (1895).

    """

    print text.translate(unaccented_map())

    # note that non-letters are passed through as is; you can use
    # encode("ascii", "ignore") to get rid of them.  alternatively,
    # you can tweak the translation dictionary to return None for
    # characters >= "\x80".

    map = unaccented_map()

    print repr(u"12\xbd inch".translate(map))
    print repr(u"12\xbd inch".translate(map).encode("ascii", "ignore"))
