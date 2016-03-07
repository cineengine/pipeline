# !/usr/bin/python
# coding: UTF-8

#    Scene wrapper for Cinema 4d Python API
#    
#    Author:  Mark Rohrer
#    Contact: mark.rohrer@gmail.com
#    Version: 0.1
#    Date:    03/07/2016
#
#    This version represents core functionality.    
#
#    Features to be added:  Checks for valid file inputs wherever files are passed.

# internal libraries
import c4d
import os.path


# HELPERS #########################################################################################

def doc():
    ''' Returns the active document. '''
    return c4d.documents.GetActiveDocument()


def new():
    ''' Create a new empty document. '''
    c4d.CallCommand(12094, 12094)
    return


def open( file_=None ):
    ''' Open the specified scene.  If no file is specified, open a dialog. '''
    if (file_):
        c4d.documents.LoadFile(file_)
    else:
        c4d.CallCommand(12095, 12095)


def save( file_=None ):
    ''' Saves the current scene. '''
    c4d.CallCommand(12098, 12098)
    return


def saveAs( file_=None ):
    ''' Saves the current scene with a new name. '''
    # Explicit output path / name
    if (file_):
        save_path = os.path.dirname(file_)
        save_file = os.path.basename(file_)

        doc().SetDocumentPath(save_path)
        doc().SetDocumentName(save_file)

        c4d.CallCommand(12098, 12098)

    # Dialog
    else:
        c4d.CallCommand(12218, 12218)
    return


def close():
    ''' Closes the current scene. '''
    c4d.CallCommand(12664, 12664)
    return


# INITIALIZERS ####################################################################################

def init():
    ''' Init scene for pipeline stuff. '''
    return


def setOutput(output_path = '', multipass_path = ''):
    ''' A generic (non-pipeline-specific) function that sets up basic parameters for rendering. '''
    res    = (1280, 720)
    frate  = 60
    aspect = 1.7777
    doc_   = doc()
    rd     = doc_.GetActiveRenderData()

    # GLOBALS
    # Output paths
    rd[c4d.RDATA_PATH]            = output_path
    # Resolution & frame rate
    rd[c4d.RDATA_XRES]            = res[0]
    rd[c4d.RDATA_YRES]            = res[1]
    rd[c4d.RDATA_LOCKRATIO]       = True
    rd[c4d.RDATA_FILMASPECT]      = aspect
    rd[c4d.RDATA_FILMPRESET]      = c4d.RDATA_FILMPRESET_HDTV
    rd[c4d.RDATA_FRAMERATE]       = frate
    # Alpha channel    
    rd[c4d.RDATA_ALPHACHANNEL]    = True
    rd[c4d.RDATA_SEPARATEALPHA]   = False
    rd[c4d.RDATA_STRAIGHTALPHA]   = True
    # Format options    
    rd[c4d.RDATA_FORMAT]          = c4d.FILTER_PNG
    rd[c4d.RDATA_FORMATDEPTH]     = c4d.RDATA_FORMATDEPTH_16
    # Frame padding & extension
    rd[c4d.RDATA_NAMEFORMAT]      = c4d.RDATA_NAMEFORMAT_6
    # AA Sampling overrides
    rd[c4d.RDATA_ANTIALIASING]    = c4d.RDATA_ANTIALIASING_BEST
    rd[c4d.RDATA_AAFILTER]        = c4d.RDATA_AAFILTER_ANIMATION
    rd[c4d.RDATA_AAMINLEVEL]      = c4d.RDATA_AAMINLEVEL_2
    rd[c4d.RDATA_AAMAXLEVEL]      = c4d.RDATA_AAMAXLEVEL_8
    # Raytracing overrides
    rd[c4d.RDATA_RAYDEPTH]        = 5
    rd[c4d.RDATA_REFLECTIONDEPTH] = 2
    rd[c4d.RDATA_SHADOWDEPTH]     = 2
    # Miscellaneous
    rd[c4d.RDATA_TEXTUREERROR]    = False

    # MULTIPASS
    # Output paths
    rd[c4d.RDATA_MULTIPASS_FILENAME] = multipass_path
    # Format options
    rd[c4d.RDATA_MULTIPASS_SAVEFORMAT] = c4d.FILTER_PNG
    rd[c4d.RDATA_MULTIPASS_SAVEDEPTH]  = c4d.RDATA_FORMATDEPTH_16

    # MAKE MULTIPASS LAYERS
    passes = {
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
    }

    for mp in passes:
        mp_obj = c4d.BaseList2D(c4d.Zmultipass)
        mp_obj.GetDataInstance()[c4d.MULTIPASSOBJECT_TYPE] = mp
        rd.InsertMultipass(mp_obj)

    c4d.EventAdd()


# BUILDERS ########################################################################################

def merge( file_=None ):
    ''' Imports a file into the scene. '''
    if (file_):
        c4d.documents.LoadFile(file_)
    else:
        c4d.CallCommand(12096, 12096)
    return


def xref( file_=None ):
    ''' References a file into the scene via dialog. Note that currently there is a limitation that 
    does not allow for XRefs to be linked through the Python API. '''
    # Dialog
    c4d.CallCommand(1025763, 1025763)
    return


def render():
    ''' Submits scene to the render farm. '''
    return


