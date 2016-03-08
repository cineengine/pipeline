import c4d
import os


# NBA project parameters
NBA = {
    'res':    (1920, 1080),
    'frate':  60,
    'bty_passes': [
        c4d.VPBUFFER_DIFFUSE,
        c4d.VPBUFFER_SPECULAR,
        c4d.VPBUFFER_REFLECTION,
        c4d.VPBUFFER_TRANSPARENCY,
        c4d.VPBUFFER_ILLUMINATION
        ],
    'util_passes': [
        c4d.VPBUFFER_AMBIENTOCCLUSION,
        c4d.VPBUFFER_MAT_NORMAL,
        c4d.VPBUFFER_MAT_UV,
        c4d.VPBUFFER_MOTIONVECTOR,
        c4d.VPBUFFER_DEPTH
        ],
    'folders': {
        'ae': [],
        'c4d': ['tex', 'export', 'backup'],
        'cam': [],
        'maya': [],
        'nuke': [],
        'qt': [],
        'render_2d': ['prerenders'],
        'render_3d': []
        },
    'layers': [
        'btyMain',
        'utilMain'
        ]
}


PROJECTS = {
    'NBA_2016': NBA
}



def init():
	''' Create project folders for a new project. '''
	return



