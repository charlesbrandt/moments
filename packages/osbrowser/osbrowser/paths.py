import os

#unless defined elsewhere, 
#will assume all paths passed in to Node objects are relative to this dir:
relative_prefix = ''
local_path = u'./'
log_path = u'./'
sort_config = 'alpha'

config_log_in_outgoing = False
config_log_in_media = False

try:
    #if not using in pylons, can define manually above
    from pylons import config
    if config.has_key('local_path'):
        local_path = unicode(config['local_path'])
    if config.has_key('log_local_path'):
        log_path = unicode(config['log_local_path'])
        config_log_in_outgoing = True
    if config.has_key('log_in_media') and config['log_in_media'] == "True":
        config_log_in_media = True
    if config.has_key('sort_order'):
        sort_config = config['sort_order']
    if config.has_key('relative_prefix'):
        relative_prefix = config['relative_prefix']
except:
    config = {}

