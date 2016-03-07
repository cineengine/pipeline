# !/usr/bin/python
# coding: UTF-8

#    Object wrapper for Cinema 4d Python API
#    - This is a series of helper functions for simplifying manipulation of C4D BaseObjects
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


def visible( v=None, r=None, obj_=None ):
    ''' Sets the visibility of an object. 'v' for viewport, and 'r' for rendering. '''
    vis = {
        True:  c4d.MODE_ON,
        False: c4d.MODE_OFF,
        None:  c4d.MODE_UNDEF
    }
    # Get selection if no object is passed
    if not (obj_):
        obj_ = core.ls()
    # If a flag is passed, set it
    for o in obj_:
        o.SetEditorMode(vis[v])
        o.SetRenderMode(vis[r])
    return