# !/usr/bin/python
# coding: UTF-8

#    Core wrapper for Cinema 4d Python API
#    - This wraps C4D functionality of a broad range of common operations into a pythonic syntax
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
from pipeline.c4d import scene


def ls( regex=False, type_=c4d.BaseObject, obj_=None ):
    ''' Returns a list of objects of specified type (default is BaseObject) that are either 
        currently selected, or passed by object reference. Both types are validated before 
        being returned as a list.'''
    # Get selection if no object reference is passed
    if not (obj_):
        obj_ = scene.doc().GetSelection()

    # If a string is passed to obj_, the command will search the scene for it. 
    # Optional 'guess' flag will match based on regex (i assume)
    elif (isinstance(obj_, str)):
        if not (regex):
            obj_ = scene.doc().SearchObject(obj_)
        elif (regex):
            obj_ = scene.doc().SearchObjectInc(obj_)

    # If a passed object is not already a list, we force the recast
    if not (isinstance(obj_, list)):
        obj_ = [obj_]
    
    # Cull any selected elements that don't match the specified object type
    for o in obj_:
        if not (isinstance(o, type_)):
            obj_.remove(o)
        else: continue

    if obj_ == []:
        obj_ = None

    # Returns a list of the specified object type
    return obj_


def visible( v=None, r=None, obj_=None ):
    ''' Sets the visibility of an object. 'v' for viewport, and 'r' for rendering. '''
    vis = {
        True:  c4d.MODE_ON,
        False: c4d.MODE_OFF,
        None:  c4d.MODE_UNDEF
    }
    # Get selection if no object is passed
    if not (obj_):
        obj_ = ls()
    # If a flag is passed, set it
    for o in obj_:
        o.SetEditorMode(vis[v])
        o.SetRenderMode(vis[r])
    return

