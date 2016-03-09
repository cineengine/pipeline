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
from pipeline.c4d import ops    # operations library


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
    take_data = scene.doc().GetTakeData()
    # Add the take and name it
    take = take_data.AddTake(name, parent=None, cloneFrom=None)
    # Add the default override groups to the take
    for og_ in OVERRIDE_GROUPS:
        og = override(take, og_)
        # Add the compositing tag for overriding
        tag = og.AddTag(take_data, c4d.Tcompositing, mat=None)
        tag.SetName('VISIBILITY_OVERRIDE')
        # ... and set the default values
        ops.setCompositingTag( tag, og_ )
    # If flagged, set the current take as active
    if (set_active): take_data.SetCurrentTake(take)

    c4d.EventAdd()
    return take


def override( take, name=None ):
    ''' Adds an override group to a specified take. '''
    og = take.AddOverrideGroup()
    if (name): og.SetName(name)

    c4d.EventAdd()
    return og

