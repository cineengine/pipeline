# !/usr/bin/python
# coding: UTF-8

#    Operations wrapper for Cinema 4d Python API
#    -  These are specific pipeline operations that utilize helper functions found throughout the 
#       other modules of this package.  They are fairly pipeline-specific.
#    
#    Author:  Mark Rohrer
#    Contact: mark.rohrer@gmail.com
#    Version: 0.1
#    Date:    03/08/2016
#
#    This version is still in progress.    
#
#    Features to be added:  a lot

# internal libraries
import c4d
import os.path
# custom libraries
from pipeline.c4d import core
from pipeline.c4d import project
from pipeline.c4d import component
from pipeline.c4d import scene


def setOutput( output_path='' ):
    ''' A generic (non-pipeline-specific) function that sets up basic parameters for rendering. 
    Specifics are pulled from 'project' global parameters module.'''
    doc    = scene.doc()
    proj   = project.DEFAULT
    res    = (proj['res'][0], proj['res'][1])
    frate  = proj['frate']
    aspect = 1.7777
    rd     = c4d.documents.RenderData()

    # GLOBAL SETTINGS
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

    # MULTIPASS
    # Output paths
    if not (output_path == ''):
        rd[c4d.RDATA_MULTIPASS_FILENAME] = os.path.join(output_path, 'passes')
    # Format options
    rd[c4d.RDATA_MULTIPASS_SAVEFORMAT] = c4d.FILTER_PNG
    rd[c4d.RDATA_MULTIPASS_SAVEDEPTH]  = c4d.RDATA_FORMATDEPTH_16
    # Raytracing overrides
    rd[c4d.RDATA_RAYDEPTH]        = 5
    rd[c4d.RDATA_REFLECTIONDEPTH] = 2
    rd[c4d.RDATA_SHADOWDEPTH]     = 2
    # Miscellaneous
    rd[c4d.RDATA_TEXTUREERROR]    = True

    for mp in proj['passes']:
        mp_obj = c4d.BaseList2D(c4d.Zmultipass)
        mp_obj.GetDataInstance()[c4d.MULTIPASSOBJECT_TYPE] = mp
        rd.InsertMultipass(mp_obj)

    rd.SetName('DEFAULT')

    doc.InsertRenderData(rd)
    doc.SetActiveRenderData(rd)
    c4d.EventAdd()
    return


def setTakes():
    ''' Makes the default takes (render layers) and overrides for the specified project. '''
    proj = project.DEFAULT
    for lyr in proj['layers']:
        take(lyr)
    return


def sortTakes():
    ''' Sorts objects into takes (via override groups) using sorting logic stored in a proj database.'''
    sort_dict = project.NBA_SORT
    td = scene.doc().GetTakeData()
    # Parse the sorting dictionary into lists of objects
    for layer_, sort in sort_dict.iteritems():
        for tag_ in sort['rgb']:
            rgba_obj = [o.GetObject() for o in core.lsTags(name=tag_, typ=c4d.Tannotation) if not tag_=='']
        for tag_ in sort['pvo']:
            pvo_obj = [o.GetObject() for o in core.lsTags(name=tag_, typ=c4d.Tannotation) if not tag_=='']
        for tag_ in sort['occ']:
            occ_obj = [o.GetObject() for o in core.lsTags(name=tag_, typ=c4d.Tannotation) if not tag_=='']
        for tag_ in sort['off']:
            off_obj = [o.GetObject() for o in core.lsTags(name=tag_, typ=c4d.Tannotation) if not tag_=='']
        # Make the layer for sorting
        layer = component.take(layer_, set_active=True)
        start = layer.GetFirstOverrideGroup()
        # Add the sorted objects to their respective render layers / takes
        for og in core.ObjectIterator(start):
            if og.GetName() == 'bty':
                for obj in rgba_obj:
                    og.AddToGroup(td, obj)
            elif og.GetName() == 'pv_off':
                for obj in pvo_obj:
                    og.AddToGroup(td, obj)
            elif og.GetName() == 'black_hole':
                for obj in occ_obj:
                    og.AddToGroup(td, obj)
            elif og.GetName() == 'disable':
                for obj in off_obj:
                    og.AddToGroup(td, obj)
