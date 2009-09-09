import os

#local_music_path = u'./'
#local_music_path = u"/home/charles/charles/media/binaries/music"
#local_music_path = u"/charles/media/binaries/music"

#this will make them all relative
local_music_path = u''
local_music_path = u'/c/media/binaries'

try:
    #if not using in pylons, can define manually above
    from pylons import config
    if config.has_key('music_path'):
        local_music_path = config['music_path']
except:
    pass

    #('\/Users\/charles\/Music\/iTunes\/iTunes Music\/', os.path.join(local_music_path, 'from/tessa_bent/')),

#/Volumes/MUSIC/cds-converted/LCD Soundsystem/Sound of Silver/LCD Soundsystem-Sound of Silver-07-Watch the Tapes.mp3

path_updates = [
    ('file:\/\/localhost', ''),
    #('\/charles\/media\/binaries\/music', os.path.join(local_music_path, 'cds')),

    ('/home/ubuntu/charles/', local_music_path),
    ('\/Volumes\/MUSIC', local_music_path),
    ('\/media\/music\/music', local_music_path),
    ('\/Volumes\/Music', local_music_path),
    ('\/Volumes\/music-1', local_music_path),
    ('\/Volumes\/music', local_music_path),
    ('I:\/mp3', local_music_path),
    ('E:', local_music_path),
    ('G:', local_music_path),

    ('\/Users\/music\/Music\/iTunes\/iTunes Music', local_music_path),
    ('music\/Compilations', 'music/cds/Compilations'),
    #few others like above... just edit

    ('cybernetic_broadcasting_system', 'music/cybernetic_broadcasting_system'),
    ('cybernetic_broadcasting_system\/duplicates', 'cybernetic_broadcasting_system/everything'),
    ('music\/cybernetic_broadcasting_system\/good', 'music/cybernetic_broadcasting_system/everything'),

    ('from_people', 'from'),
    ('from\/tessa', 'music/from/tessa'),
    ('from\/jason_raibley', 'music/from/jason_raibley'),
    ('from\/lee_runyan', 'music/from/lee_runyan'),
    ('music\/from\/geoff_edelmann', 'music-other/from/geoff_edelmann'),
    ('from\/geoff_edelmann', 'music-extended/from/geoff_edelmann'),
    ('from\/brian_beaver', 'music-other/from/brian_beaver'),
    ('music\/from\/brian_beaver', 'music-other/from/brian_beaver'),
    ('music\/from\/jesse_viehe', 'music-other/from/jesse_viehe'),
    ('music\/from\/matt_fitzgerald', 'music-other/from/matt_fitzgerald'),
    ('media\/binaries\/music-extended\/from', 'media/binaries/music-other/from'),
    
    ('music\/shared_music_compilations', 'music-other/shared_music_compilations'),
    ('music\/ipod_recovered', 'music-other/ipod_recovered'),
    ('cds-other', 'music-other/cds-other'),
    ('music\/cds-other', 'music-other/cds-other'),
    ('music\/cds-library', 'music-extended/from-library'),
    ('cds-library', 'music-extended/from-library'),
    ('music\/labels', 'music-other/labels'),
    ('music\/cds-converted', 'music/cds'),
    ('cds-converted', 'music/cds'),
    ('pod_casts', 'podcasts'),

    (r'\\', '/'),
    ('\ \(1\)', ''),
    #('\ \(2\)', ''),
    ('^vinyl', os.path.join(local_music_path, 'vinyl')),
    ('vinyl\/vinyl_converted\/mp3_versions', 'music/vinyl/mp3'),
    ('cds\/Black\ Cat\ Music\/', 'people_i_know/omar_perez/Black Cat Music/'),
    #('Converted Music', 'cds'),
    ('labels', 'music-other/labels'),
    ]
