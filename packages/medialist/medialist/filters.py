"""
# this file provides a place to keep track of changes to the layout of your
# media drives and have medialists automatically update old logs to use the
# new layout

# this is a special 'meta' version of filters
# that will check the config to see if there is
# a system specific one specified in the pylons config
"""

import os

#local_music_path = u'./'
#local_music_path = u"/c/code/python/pose/pose/public/test/media/music"

#this will make them all relative
local_music_path = u''

try:
    #if not using in pylons, can define manually above
    from pylons import config
    if config.has_key('path_updates'):
        path_updates = config['path_updates']
    elif config.has_key('music_path'):
        local_music_path = config['music_path']
        path_updates = [
            ('file:\/\/localhost', ''),
            ('\/Volumes\/MUSIC', local_music_path),
            ('\/Volumes\/Music', local_music_path),
            ('\/Volumes\/music', local_music_path),
            ('^\/media\/music', local_music_path),
            (r'\\', '/'),
            
            ]
    else:
        path_updates = []

except:
    path_updates = []

