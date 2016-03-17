#    Temporary project 'database' for c4d pipeline development
#    
#    Author:  Mark Rohrer
#    Contact: mark.rohrer@gmail.com
#    Version: 0.1
#    Date:    03\\09\\2016
#
#    This will eventually be migrated to a document-based database format   
#
#    Features to be added: none

import c4d
from pipeline.c4d import error

# Default parameters
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

OVERRIDE_GROUPS = [
    'bty',
    'pv_off',
    'black_hole',
    'disable'
    ]

# NBA sorting parameters
NBA_SORT = {
    'homeLogo': {
        'rgb' : ['home_logo_geo'],
        'occ' : ['home_env_geo'],
        'pvo' : [''],
        'off' : ['']
    },
    'homeEnv': {
        'rgb' : ['home_env_geo'],
        'occ' : [''],
        'pvo' : ['home_logo_geo'],
        'off' : ['']
    },
    'showLogo': {
        'rgb' : ['show_logo_geo'],
        'occ' : [''],
        'pvo' : [''],
        'off' : ['']
    }
}


# NBA project parameters
NBA = {
    'project' :      '\\\\cagenas\\Workspace\\MASTER_PROJECTS\\NBA_2016\\001_PROJECTS\\000_Animation',
    'assets'  :      '\\\\cagenas\\Workspace\\MASTER_PROJECTS\\NBA_2016\\004_TOOLBOX\\001_3D_ASSETS',
    'teams'   :      '\\\\cagenas\\Workspace\\MASTER_PROJECTS\\NBA_2016\\004_TOOLBOX\\002_3D_TEAMS',
    'res'     :      DEFAULT['res'],
    'frate'   :      DEFAULT['frate'],
    'passes'  :      DEFAULT['passes'],
    'layers'  :      DEFAULT['layers'],
    'sort'    :      NBA_SORT,
    'folders' :      {
        'ae'  :      [],
        'c4d' :      ['tex', 'export', 'backup'],
        'cam' :      [],
        'maya':      [],
        'nuke':      [],
        'qt'  :      [],
        'render_2d': ['prerenders'],
        'render_3d': []
        }

}


# Folder-to-database-object converter
PRODUCTIONS = {
    'NBA_2016': NBA,
}


# GETTERS ##########################################################################################
def getProduction():
    ''' Infers the project based on where the current scene is located. '''
    scene_path = core.doc().GetDocumentPath()
    scene_path = scene_path.split('\\')
    prod_      = scene_path[3]

    try:
        prod   = PRODUCTIONS[proj_]
        return prod
    except KeyError:
        raise error.PipelineError(3)





