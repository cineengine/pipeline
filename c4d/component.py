# !/usr/bin/python
# coding: UTF-8

#    Components (sub-objects) wrapper for Cinema 4d Python API
#    - This is a set of helper functions for operating on non-geometry components in C4D (tags, 
#      deformers, effectors, etc)
#    
#    Author:  Mark Rohrer
#    Contact: mark.rohrer@gmail.com
#    Version: 0.1
#    Date:    03/07/2016
#
#    This version is still in progress.    
#
#    Features to be added:  a lot

# internal libraries
import c4d
# custom libraries
from pipeline.c4d import core
from pipeline.c4d import scene


OVERRIDE_GROUPS = [
    'bty',
    'pv_off',
    'black_hole',
    'disable'
    ]


def tag( typ=None, name=None, obj_=None ):
    ''' Creates a tag on the selected (or specified) object. For tag types, see:
    https://developers.maxon.net/docs/Cinema4DPythonSDK/html/types/tags.html '''
    # Get the selected object, if none is passed
    obj_ = core.ls(obj_)
    # Empty return container
    tags = []
    # Make a tag for each object
    for o in obj_:
        tag = o.MakeTag(typ)
        # Add the tag to the return list
        tags.append(tag)
        # Name the tag
        if name:
            tag[c4d.ID_BASELIST_NAME] = name

    c4d.EventAdd()
    return tags


def take( name=None, set_active=False ):
    ''' Create a new take / render layer. '''
    # TakeData is a singleton container for all the takes in the scene
    td = scene.doc().GetTakeData()

    # Iterate over all takes to see if one with that name already exists
    main = td.GetMainTake()
    for take in core.ObjectIterator(main):
        if (take.GetName() == name):
            return take

    # Otherwise add the take and name it
    take = td.AddTake(name, parent=None, cloneFrom=None)

    # Add the default override groups to the take
    for og_ in OVERRIDE_GROUPS:
        og = override(take, og_)
        # Add the compositing tag for overriding
        tag = og.AddTag(td, c4d.Tcompositing, mat=None)
        tag.SetName('VISIBILITY_OVERRIDE')
        # ... and set the default values
        setCompositingTag( tag, og_ )

    # If flagged, set the current take as active
    if (set_active): td.SetCurrentTake(take)

    c4d.EventAdd()
    return take


def override( take, name=None ):
    ''' Adds an override group to a specified take. '''
    og = take.AddOverrideGroup()
    if (name): og.SetName(name)

    c4d.EventAdd()
    return og


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
