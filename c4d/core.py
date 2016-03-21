# !/usr/bin/python
# coding: UTF-8

#    Core wrapper for Cinema 4d Python API
#    - This wraps C4D functionality of a broad range of object operations with common conditionals
#      and error handling.  These functions have no other dependencies besides Maxon's c4d module.
#    
#    Author:  Mark Rohrer
#    Contact: mark.rohrer@gmail.com
#    Version: 0.2
#    Date:    03/17/2016
#
#    This version is still in progress.    
#
#    Features to be added:  a lot

import os.path
# internal libraries
import c4d
from c4d.modules import render


OVERRIDE_GROUPS = [
    'bty',
    'pv_off',
    'black_hole',
    'disable'
    ]


# SIMPLE OPERATIONS ###############################################################################
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


def saveAs( file_ ):
    ''' Saves the current scene with a new name. '''
    # Explicit output path / name
    if (file_):
        save_path = os.path.dirname(file_)
        save_file = os.path.basename(file_)

        doc().SetDocumentPath(save_path)
        doc().SetDocumentName(save_file)

        c4d.CallCommand(12098, 12098)

    # Dialog
    else: pass
    return


def close():
    ''' Closes the current scene. '''
    c4d.CallCommand(12664, 12664)
    return


def doc():
    ''' Returns the active document. '''
    return c4d.documents.GetActiveDocument()


def merge( file_=None ):
    ''' Imports a file into the scene. '''
    if (file_):
        c4d.documents.LoadFile(file_)
    else:
        c4d.CallCommand(12096, 12096)
    return


# FLAGS & TAGS ####################################################################################
def visibility( obj_=None, v=None, r=None ):
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


def tag( obj_=None, typ=None, name=None ):
    ''' Creates a tag on the selected (or specified) object. For tag types, see:
    https://developers.maxon.net/docs/Cinema4DPythonSDK/html/types/tags.html '''
    # Parse the passed object, or get the current selection
    obj = ls(obj=obj_)
    # Empty return container
    tags = []
    # Make a tag for each object
    for o in obj:
        tag = o.MakeTag(typ)
        # Add the tag to the return list
        tags.append(tag)
        # Name the tag
        if name:
            tag[c4d.ID_BASELIST_NAME] = name

    c4d.EventAdd()
    return tags


# MATERIALS & TEXTURES ############################################################################
def changeTexture( mat, tex_path, channel=c4d.MATERIAL_COLOR_SHADER ):
    ''' Changes the texture on a material's specified channel.  Defaults to the color channel.
    C:\Program Files\MAXON\CINEMA 4D R17\resource\modules\c4dplugin\description\mmaterial.h '''
    if isinstance(mat, str):
        for mat_ in MaterialIterator(doc()):
            if mat_.GetName() == mat:
                mat = mat_
                break

    if not isinstance(mat, c4d.Material):
        return

    if type(channel) == int:
        tex = c4d.BaseList2D(c4d.Xbitmap)
        tex[c4d.BITMAPSHADER_FILENAME] = tex_path
        mat[channel] = tex
        mat.InsertShader(tex)

    elif channel == ('reflect' or 'reflection'):
        refl_shd = mat.GetAllReflectionShaders()
        for rs in refl_shd:
            rs[c4d.BITMAPSHADER_FILENAME] = tex_path

    mat.Message(c4d.MSG_UPDATE)
    mat.Update(1,1)
    c4d.EventAdd()
    return True


def changeColor( mat, vector, channel=c4d.MATERIAL_COLOR_COLOR ):
    ''' Changes the color on a material's specified channel.  Defaults to the diffuse color channel.'''
    if isinstance(mat, str):
        for mat_ in MaterialIterator(doc()):
            if mat_.GetName() == mat:
                mat = mat_
                break

    if not isinstance(mat, c4d.Material):
        return

    if type(channel) == int:
        mat[channel] = vector

    mat.Message(c4d.MSG_UPDATE)
    mat.Update(1,1)
    c4d.EventAdd()
    return True



# TAKE / RENDER LAYER UTILITIES ###################################################################
def take( name=None, set_active=False ):
    ''' Create a new take / render layer. '''
    # TakeData is a singleton container for all the takes in the scene
    td = doc().GetTakeData()

    # Iterate over all takes to see if one with that name already exists
    main = td.GetMainTake()
    for take in ObjectIterator(main):
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
    take.SetChecked(True)

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


def createRenderData( rd, name ):
    ''' Inserts a RenderData document into the scene, overwriting any other document with the same
    name.  Seriously, fuck C4D sometimes. '''
    start = doc().GetFirstRenderData()
    for rd_ in ObjectIterator(start):
        if rd_.GetName() == name:
            rd_.Remove()
    rd.SetName(name)
    doc().InsertRenderData(rd)
    doc().SetActiveRenderData(rd)
    c4d.EventAdd()
    return


# OBJECT-PARSING / SELECTION UTILITIES ############################################################
def ls( obj=None, typ=c4d.BaseObject, name=None ):
    ''' Returns a list of BaseObjects of specified type that are either currently selected,
        or passed by object reference. Both types are validated before being returned as a list.'''
    # Get selection if no object reference is passed
    if not (name or obj):
        obj = doc().GetSelection()

    # If a string is passed to name, the command will attempt to locate it by exact name.
    # Since C4D allows objects to have the same name, it will always return a list
    elif (isinstance(name, str)):
        start = doc().GetFirstObject()
        obj   = []
        for o in ObjectIterator(start):
            if o.GetName() == name:
                obj.append(o)

    # If a passed object is not already a list, we force the recast
    if not (isinstance(obj, list)):
        obj = [obj]
    
    # Cull any selected elements that don't match the specified object type
    for o in obj:
        if not (isinstance(o, typ)):
            obj.remove(o)
        else: continue

    # Returns a list of the specified object type, or none for an empty list
    if obj == []:
        obj = None
    return obj


def lsTags( obj=None, name=None, typ=None ):
    ''' Returns a list of tags in the scene.  Search parameters based on tag type or tag name.  At
    least one must be included in the command. '''
    if (name==None) and (typ==None):
        return
    return_tags = []
    # If an object reference is passed, search only its heirarchy
    if not (obj): obj = doc().GetFirstObject()

    for o in ObjectIterator(obj):
        # Search each object for tags
        for tag in TagIterator(o):
            # Compare the tag to requirements
            if (tag.GetName() == name) and (tag.GetType() == typ):
                return_tags.append(tag)
            elif (tag.GetName() == None) and (tag.GetType() == typ):
                return_tags.append(tag)
            elif (tag.GetName() == name) and (tag.GetType() == None):
                return_tags.append(tag)

    return return_tags


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
