# !/usr/bin/python
# coding: UTF-8

#    Core wrapper for Cinema 4d Python API
#    - This wraps C4D functionality of a broad range of object operations with common conditionals
#      and error handling.  (Selection, visibility, etc.)
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


def ls( typ=c4d.BaseObject, obj_=None ):
    ''' Returns a list of BaseObjects of specified type that are either currently selected,
        or passed by object reference. Both types are validated before being returned as a list.'''
    # Get selection if no object reference is passed
    if not (obj_):
        obj = scene.doc().GetSelection()

    # If a string is passed to obj_, the command will attempt to locate it by exact name. 
    # If an exact match isn't found, it will expand the search parameters to near-matches
    # (Obviously this is somewhat unreliable and will require further testing.)
    elif (isinstance(obj_, str)):
        obj = scene.doc().SearchObject(obj_)
        if not obj:
            obj = scene.doc().SearchObjectInc(obj_)

    # If a passed object is not already a list, we force the recast
    if not (isinstance(o, list)):
        obj = [obj]
    
    # Cull any selected elements that don't match the specified object type
    for o in obj:
        if not (isinstance(o, c4d.BaseObject)):
            obj.remove(o)
        else: continue

    if obj == []:
        obj = None

    # Returns a list of the specified object type
    return obj


def lsTags( name=None, typ=None ):
    ''' Returns a list of tags in the scene.  Search parameters based on tag type or tag name.  At
    least one must be included in the command. '''
    if (name==None) and (typ==None):
        return
    return_tags = []
    # Search all objects in the scene for tags
    first = scene.doc().GetFirstObject()
    for obj in ObjectIterator(first):
        # Search each object for tags
        for tag in TagIterator(obj):
            # Compare the tag to requirements
            if (tag.GetName() == name) and (tag.GetType() == typ):
                return_tags.append(tag)
            elif (tag.GetName() == None) and (tag.GetType() == typ):
                return_tags.append(tag)
            elif (tag.GetName() == name) and (tag.GetType() == None):
                return_tags.append(tag)

    return return_tags


def visiblity( v=None, r=None, obj_=None ):
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


### The following iterators were borrowed directly from Martin Weber via cgrebel.com.
### All credit goes to him -- thank you Martin! -- I could not find any license usage for this code.
### http://cgrebel.com/2015/03/c4d-python-scene-iterator/

class ObjectIterator:
    ''' Iterates over all BaseObjects below the input object in the hierarchy, including children. '''
    def __init__(self, baseObject):
        self.baseObject = baseObject
        self.currentObject = baseObject
        self.objectStack = []
        self.depth = 0
        self.nextDepth = 0

    def __iter__(self):
        return self

    def next(self):
        if self.currentObject == None :
            raise StopIteration

        obj = self.currentObject
        self.depth = self.nextDepth

        child = self.currentObject.GetDown()
        if child :
            self.nextDepth = self.depth + 1
            self.objectStack.append(self.currentObject.GetNext())
            self.currentObject = child
        else :
            self.currentObject = self.currentObject.GetNext()
            while( self.currentObject == None and len(self.objectStack) > 0 ) :
                self.currentObject = self.objectStack.pop()
                self.nextDepth = self.nextDepth - 1
        return obj


class TagIterator:
    ''' Iterates over all tags on a given object. '''
    def __init__(self, obj):
        currentTag = None
        if obj :
            self.currentTag = obj.GetFirstTag()

    def __iter__(self):
        return self

    def next(self):
        tag = self.currentTag
        if tag == None :
            raise StopIteration

        self.currentTag = tag.GetNext()
        return tag


class MaterialIterator:
    ''' Iterates over all materials in a given document. '''
    def __init__(self, doc):
        self.doc = doc
        self.currentMaterial = None
        if doc == None : return
        self.currentMaterial = doc.GetFirstMaterial()

    def __iter__(self):
        return self

    def next(self):
        if self.currentMaterial == None :
            raise StopIteration

        mat = self.currentMaterial
        self.currentMaterial = self.currentMaterial.GetNext()
        return mat