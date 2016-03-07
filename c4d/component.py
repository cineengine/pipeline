# !/usr/bin/python
# coding: UTF-8

#    Components (sub-objects) wrapper for Cinema 4d Python API
#    - This is a catch-all for any non-geometry component in C4D (tags, deformers, effectors, etc)
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


def tag( obj_=None, type_=None, name=None ):

    ''' Creates a tag on the selected (or specified) object. '''
    # Get the selected object, if none is passed
    obj_ = core.ls(obj_)
    # Empty return container
    tags = []
    # Make a tag for each object
    for o in obj_:
        tag = o.MakeTag(type_)
        # Add the tag to the return list
        tags.append(tag)
        # Name the tag
        if name:
            tag[c4d.ID_BASELIST_NAME] = name

    c4d.EventAdd()

    return tags


def findTag():
    return
