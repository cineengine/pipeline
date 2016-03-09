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

reload(core)
reload(project)
reload(component)
reload(scene)


def setCompositingTag( tag, preset, reset=False ):
    ''' Sets a compositing tag with preset values for primary visibility, etc.'''
    # Some overrides take place on the override group, so we store tha
    og = tag.GetObject()
    # In the event that this isn't called at creation, we first reset the affected values to default
    if (reset):
        og.SetEditorMode(c4d.MODE_UNDEF)
        og.SetRenderMode(c4d.MODE_UNDEF)
        tag[c4d.COMPOSITINGTAG_CASTSHADOW] = True
        tag[c4d.COMPOSITINGTAG_RECEIVESHADOW] = True
        tag[c4d.COMPOSITINGTAG_SEENBYCAMERA] = True
        tag[c4d.COMPOSITINGTAG_SEENBYRAYS] = True
        tag[c4d.COMPOSITINGTAG_SEENBYGI] = True
        tag[c4d.COMPOSITINGTAG_SEENBYTRANSPARENCY] = True
        tag[c4d.COMPOSITINGTAG_MATTEOBJECT] = False
        tag[c4d.COMPOSITINGTAG_MATTECOLOR] = c4d.Vector(0,0,0)

    # Now the business
    if (preset) == 'bty':
        pass
    elif (preset) == 'pv_off':
        tag[c4d.COMPOSITINGTAG_CASTSHADOW] = True
        tag[c4d.COMPOSITINGTAG_RECEIVESHADOW] = False
        tag[c4d.COMPOSITINGTAG_SEENBYCAMERA] = False
        tag[c4d.COMPOSITINGTAG_SEENBYRAYS] = True
        tag[c4d.COMPOSITINGTAG_SEENBYGI] = True
    elif (preset) == 'black_hole':
        tag[c4d.COMPOSITINGTAG_MATTEOBJECT] = True
        tag[c4d.COMPOSITINGTAG_MATTECOLOR] = c4d.Vector(0,0,0)
    elif (preset) == 'disable':
        og.SetEditorMode(c4d.MODE_OFF)
        og.SetRenderMode(c4d.MODE_OFF)
        tag[c4d.COMPOSITINGTAG_CASTSHADOW] = False
        tag[c4d.COMPOSITINGTAG_RECEIVESHADOW] = False
        tag[c4d.COMPOSITINGTAG_SEENBYCAMERA] = False
        tag[c4d.COMPOSITINGTAG_SEENBYRAYS] = False
        tag[c4d.COMPOSITINGTAG_SEENBYGI] = False
        tag[c4d.COMPOSITINGTAG_SEENBYTRANSPARENCY] = False

    c4d.EventAdd()
    return


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
    proj = project.NBA_SORT
    td = scene.doc().GetTakeData()

    for layer_, sort in proj.iteritems():
        for tag_ in sort['rgba']:
            rgba_obj = [o.GetObject() for o in core.lsTags(name=tag_, typ=c4d.Tannotation) if not tag_=='']
        for tag_ in sort['pvo']:
            pvo_obj = [o.GetObject() for o in core.lsTags(name=tag_, typ=c4d.Tannotation) if not tag_=='']
        for tag_ in sort['occ']:
            occ_obj = [o.GetObject() for o in core.lsTags(name=tag_, typ=c4d.Tannotation) if not tag_=='']
        for tag_ in sort['lgt']:
            lgt_obj = [o.GetObject() for o in core.lsTags(name=tag_, typ=c4d.Tannotation) if not tag_=='']

        print rgba_obj, '\n', pvo_obj, '\n', occ_obj, '\n', lgt_obj, '\n'

        layer = component.take(layer_, set_active=True)
        start = layer.GetFirstOverrideGroup()

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
