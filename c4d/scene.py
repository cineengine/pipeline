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
from c4d import gui
from os import makedirs
import os.path
# custom libraries
from pipeline.c4d import component
from pipeline.c4d import core

reload(component)
reload(core)

# HELPERS #########################################################################################

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

        core.doc().SetDocumentPath(save_path)
        core.doc().SetDocumentName(save_file)

        c4d.CallCommand(12098, 12098)

    # Dialog
    else: raise FileError(0)

    return


def increment(filename):
    ''' This function takes a valid backup file-name and searches the destination folder for the 
    next valid version increment.  Note this is a fairly 'dumb' process, but ensures that a 
    particular backup is never overwriting an existing one. '''
    if not os.path.exists(filename):
        return filename

    file_path = os.path.dirname(filename)
    file_name = os.path.basename(filename)
    file_name = file_name.split('.')
    name      = file_name[0]
    ext       = file_name[len(file_name)-1]

    if len(file_name) == 2:
        cur_vers = 1
    elif len(file_name) == 3:
        cur_vers = int(file_name[1])+1
    else:
        raise FileError(2)

    incr_name = "{}.{}.{}".format(name, str(cur_vers).zfill(4), ext)
    incr_file = os.path.join(file_path, incr_name)

    if os.path.exists(incr_file):
        incr_file = increment(incr_file)

    return incr_file


def backup():
    ''' Backs up the current scene file. '''
    scene_path  = core.doc().GetDocumentPath()
    scene_name  = core.doc().GetDocumentName()
    scene_file  = os.path.join(scene_path, scene_name)

    backup_path = os.path.join(scene_path, 'backup')
    backup_file = os.path.join(backup_path, scene_name)
    print backup_file
    backup_file = increment(backup_file)
    print backup_file

    if not os.path.exists(backup_path):
        makedirs(backup_path)

    try:
        saveAs(backup_file)
        saveAs(scene_file)
    except FileError:
        pass

    return


def close():
    ''' Closes the current scene. '''
    c4d.CallCommand(12664, 12664)
    return


# INITIALIZERS ####################################################################################
def init():
    ''' Initializes a scene for pipeline operations. '''
    # Check the scene's current status
    scene_ctrl = core.ls(name='__SCENE__')
    doc        = core.doc()
    # No control nodes exist (initialize)
    if (scene_ctrl == None):
        flag_new   = True
        scene_ctrl = c4d.BaseObject(c4d.Onull)        
        doc.InsertObject(scene_ctrl)
        scene_ctrl.SetName('__SCENE__')
        scene_tag  = component.tag(c4d.Tannotation, 'SCENE_DATA', scene_ctrl)[0]
        #doc.InsertObject(scene_tag[0])
        c4d.EventAdd()
    # One control node exists (parse it)
    elif (len(scene_ctrl)==1):
        flag_new   = False
        scene_ctrl = scene_ctrl[0]
        scene_tag  = core.lsTags(name='SCENE_DATA', typ=c4d.Tannotation, obj=scene_ctrl)[0]
    # Two+ control nodes exist (escape)
    elif (len(scene_ctrl)>1):
        raise PipelineError(1)

    if (flag_new):
        annotation   = "Project: {0}\nScene: {1}\nVersion: {2}"
        project_name = gui.RenameDialog('PROJECT_FILE_FOLDER_NAME')
        scene_name   = gui.RenameDialog('ELEMENT_NAME')
        annotation   = annotation.format(project_name, scene_name, str(1))
        scene_tag[c4d.ANNOTATIONTAG_TEXT] = annotation
    else:
        annotation = scene_tag[c4d.ANNOTATIONTAG_TEXT]

    scene_data = annoToDict(annotation)
    return scene_data


def annoToDict(tag_data):
    ''' Takes a block of text from an annotation tag field and converts it to a dictionary.'''
    a = tag_data.split('\n')
    b = {}
    for a_ in a:
        kv = a_.split(':')
        b[kv[0]] = kv[1].lstrip()
    return b


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


# ERROR HANDLING ##################################################################################
class FileError(Exception):
    def __init__(self, message, alert=True):
        super(FileError, self).__init__(message)
        self.message = message
        if (alert): self._alert()

    def _alert(self):
        notification = {
            0: 'Scene backup folder not found or could not be created.',
            1: '',
            2: 'Your scene file name is invalid.  Must be name.#.c4d or name.c4d'
        }[self.message]
        gui.MessageDialog(notification)


class PipelineError(Exception):
    def __init__(self, message, alert=True):
        super(PipelineError, self).__init__(message)
        self.message = message
        if (alert): self._alert()

    def _alert(self):
        notification = {
            0: 'No __SCENE__ object found. Has this scene been set up in the pipeline?',
            1: 'Multiple __SCENE__ objects were found. Delete any extras from merged scenes to continue.'
        }[self.message]
        gui.MessageDialog(notification)
