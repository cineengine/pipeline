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


def backup():
    ''' Backs up the current scene file. '''
    doc        = doc()
    scene_path = doc.GetDocumentPath()
    scene_name = doc.GetDocumentName()

    if not (os.path.exists(os.path.join(scene_path, scene_name))):
        return
    else:
        new_path = os.path.join(scene_path, 'backup')
        new_name = scene_name.split('.')
        new_name[0] += 'test'


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


