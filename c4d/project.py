import c4d
import os


PROJECTS = {
    'NBA_2016': NBA
}


# NBA project parameters
NBA = {
    'res':    (1920, 1080),
    'frate':  60,
    'passes': [
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
        ],
    'folders': {
        'ae': [''],
        'c4d': ['tex', 'export'],
        'cam': [''],
        'maya': ['']
        'nuke': [''],
        'qt': [''],
        'render_2d': ['prerenders'],
        'render_3d': ['']
        }
}



def init():
	''' Create project folders for a new project. '''
	return



