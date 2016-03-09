# !/usr/bin/python
# coding: UTF-8

#    Temporary project 'database' for c4d pipeline development
#    
#    Author:  Mark Rohrer
#    Contact: mark.rohrer@gmail.com
#    Version: 0.1
#    Date:    03/09/2016
#
#    This will eventually be migrated to a document-based database format   
#
#    Features to be added: none

# Default project parameters
DEFAULT = {
    'res'     : (1920, 1080),
    'frate'   : 60,
    'layers'  : ['main'],
    'passes'  : [
        c4d.VPBUFFER_DIFFUSE,
        c4d.VPBUFFER_SPECULAR,
        c4d.VPBUFFER_REFLECTION,
        c4d.VPBUFFER_TRANSPARENCY,
        c4d.VPBUFFER_ILLUMINATION,
        c4d.VPBUFFER_AMBIENTOCCLUSION,
        c4d.VPBUFFER_MAT_NORMAL,
        c4d.VPBUFFER_MAT_UV,
        c4d.VPBUFFER_MOTIONVECTOR,
        c4d.VPBUFFER_DEPTH
        ]
}

# NBA project parameters
NBA = {
    'res'     : DEFAULT['res'],
    'frate'   : DEFAULT['frate'],
    'passes'  : DEFAULT['passes'],
    'layers'  : DEFAULT['layers'],
    'folders' : {
        'ae'  : [],
        'c4d' : ['tex', 'export', 'backup'],
        'cam' : [],
        'maya': [],
        'nuke': [],
        'qt'  : [],
        'render_2d': ['prerenders'],
        'render_3d': []
        }
}

# NBA sorting parameters
NBA_SORT = {
    'homeLogo': {
        'rgba': ['home_logo_geo'],
        'occ' : ['home_env_geo'],
        'pvo' : [''],
        'lgt' : ['home_logo_lgt']
    },
    'homeEnv': {
        'rgba': ['home_env_geo'],
        'occ' : [''],
        'pvo' : ['home_logo_geo'],
        'lgt' : ['home_env_lgt']
    },
    'showLogo': {
        'rgba': ['show_logo_geo'],
        'occ' : [''],
        'pvo' : [''],
        'lgt' : ['show_logo_lgt']
    }
}


# Folder-to-database-object converter
PROJECTS = {
    'NBA_2016': NBA
}



def init():
	''' Create project folders for a new project. '''
	return



