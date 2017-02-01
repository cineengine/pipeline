# coding: UTF-8

# internal libraries
import c4d
from c4d import gui
from os import makedirs
import os.path
# custom libraries
from pipeline.c4d import core
from pipeline.c4d import database
from pipeline.c4d import status
from pipeline.c4d.gvars import *

class Scene(object):
    status       = status.SCENE_PRELOAD
    production   = ''
    project_name = ''
    scene_name   = ''
    file_path    = ''
    version      = 0
    framerate    = 0
    scene_ctrl   = None
    scene_tag    = None

    def __init__(self):
        self.init_status()
        if (self.status == status.SCENE_OK):
            self.pull_scene()
    
    def __repr__(self):
        _str_ = "\n"
        _str_ += "Production: {}\n".format(self.production)
        _str_ += "Project: {}\n".format(self.project_name)
        _str_ += "Scene: {}".format(self.scene_name)
        return _str_

    # INITIALIZATION
    @classmethod
    def init_status(self):
        ''' Sets the status of the scene and returns a copy of the status msg.'''
        # Tuple to store scene_ctrl node, scene_tag node, and status message
        scene_ctrl = core.ls(name='__SCENE__')
        # No scene_ctrl found -- must be new scene
        if (scene_ctrl == None or scene_ctrl == []):
            self.status     = status.SCENE_NEW
            return self.status
        # One scene_ctrl found -- check it for a tag
        elif (len(scene_ctrl)==1):
            scene_tag = core.lsTags(name='SCENE_DATA', typ=c4d.Tannotation, obj=scene_ctrl[0])
            if not (scene_tag):
                self.status = status.SCENE_BROKEN
                return self.status
            self.scene_ctrl = scene_ctrl[0]
            self.scene_tag  = scene_tag[0]
            self.status     = status.SCENE_OK
        # 2+ scene_ctrl found -- scene is broken
        elif (len(scene_ctrl)>1):
            self.status     = status.SCENE_BROKEN
            return self.status

    def init_new(self, prod='', scene='', proj='', framerate=30, version=1, force=False):
        """ Called on a new scene, or a scene that's being re-initialized into a new project."""
        if (prod == '' or scene == '' or proj == ''):
            msg = 'Missing production, project, or scene name. All are required to proceed.'
            gui.MessageDialog(msg, c4d.GEMB_OK)
            return False
        # check for existing scene controller
        if (self.status == status.SCENE_OK):
            if (force == True):
                self.scene_ctrl.Remove()
            else:
                # Insert error here
                return False

        self.production = prod
        self.scene_name = scene
        self.proj_name  = proj
        self.framerate  = framerate
        self.version    = version

        # create new scene controller
        self.make_scene_ctrl()
        # setup project and save
        self.make_folders()
        #scn.setTakes()
        self.push_renderdata()
        self.push_output_paths()
        #auto.relinkTextures(migrate=True)
        self.save()
        return self

    @classmethod
    def is_pipelined(self):
        self()
        if (self.status == status.SCENE_OK):
            return True
        else: return False

    # PUSH/PULL FUNCTIONS

    # A "pull" method is called to update the Python controller when something in the scene is likely to have
    # changed behind the frontend. The most common example is when the user opens a scene, or modifies the
    # scene_tag directly.
    def pull_scene(self):
        ''' Updates this object with information from the scene_tag in the active document. '''
        def tag_to_dict(tag_data):
            ''' Takes a block of text from an annotation tag field and converts it to a dictionary.'''
            a = tag_data.split('\n')
            b = {}
            for a_ in a:
                kv = a_.split(':')
                b[kv[0]] = kv[1].lstrip()
            return b
        # parse the scene tag string into a dictionary
        scene_data = tag_to_dict(self.scene_tag[c4d.ANNOTATIONTAG_TEXT])
        # populate attributes from dictionary
        self.production   = scene_data['Production']
        self.prod_data    = database.getProduction(self.production)
        self.project_name = scene_data['Project']
        self.scene_name   = scene_data['Scene']
        self.framerate    = int(scene_data['Framerate'])
        self.version      = int(scene_data['Version'])
        self.repath()

    def repath(self):
        ''' Updates internal path data for the scene when it is moved or renamed. '''
        self.file_name     = '{0}_{1}.c4d'.format(self.project_name, self.scene_name)
        self.file_folder   = os.path.join(self.prod_data['project'], self.project_name, 'c4d')
        self.backup_folder = os.path.join(self.file_folder, 'backup')
        self.file_path     = os.path.join(self.file_folder, self.file_name)

    # A "push" method updates the scene with information stored in the Python controller. Most frontend
    # operations which use this object as a mapper involve a push to the scene to update it.
    def push_scene(self):
        ''' Updates the scene_tag with new or updated data from this object. '''
        def dict_to_tag():
            out_str = ''
            out_str += 'Production: {0}\n'.format(self.production)
            out_str += 'Project: {0}\n'.format(self.project_name)
            out_str += 'Scene: {0}\n'.format(self.scene_name)
            out_str += 'Framerate: {0}\n'.format(self.framerate)
            out_str += 'Version: {0}'.format(self.version)
            return out_str
        #
        if (self.is_pipelined()):
            self.scene_tag[c4d.ANNOTATIONTAG_TEXT] = dict_to_tag()
            return True
        else:
            return False

    def push_output_paths(self):
        ''' Set render output paths for this scene.'''
        self.output_path = os.path.join(
            self.prod_data['project'],
            self.project_name,
            'render_3d',
            self.scene_name,
            'v{0}'.format(str(self.version).zfill(3)),
            '$take',
            '{0}_{1}'.format(self.scene_name, '$take')
            )
        self.multi_path = os.path.join(
            self.prod_data['project'],
            self.project_name,
            'render_3d',
            self.scene_name,
            'v{0}'.format(str(self.version).zfill(3)),
            '$take_passes',
            '{0}_{1}'.format(self.scene_name, '$take')
            )
        core.setOutputPaths(self.output_path, self.multi_path)
        return True

    def push_renderdata(self, preset_name='Default'):
        '''Load selected RenderData from a master library of production presets.'''
        preset = c4d.documents.LoadDocument(PRESETS_PATH.format(self.production, preset_name), c4d.SCENEFILTER_0)
        new_rd = preset.GetFirstRenderData()
        core.createRenderData(new_rd, preset_name)
        doc = c4d.documents.GetActiveDocument()
        doc.SetActiveRenderData(new_rd)
        return True

    # BUILDERS / CREATORS
    # These methods use the Python obj000ct as an intermediary to create new objects within Cinema4D or
    # the filesystem    
    def make_takes(self):
        ''' Makes the default takes (render layers) and overrides for the specified production. '''
        td = core.doc().GetTakeData()
        for take_ in self.prod_data['layers']:
            take = core.take(take_, set_active=True)
            #take.SetChecked(True)
            # Add the default override groups to the take
            for og_ in core.OVERRIDE_GROUPS:
                og = core.override(take, og_)
                # Add the compositing tag for overriding
                tag = og.AddTag(td, c4d.Tcompositing, mat=None)
                tag.SetName('VISIBILITY_OVERRIDE')
                # ... and set the default values
                core.setCompositingTag( tag, og_ )
        return

    def make_folders(self, check_project=False):
        ''' Makes folders for a new project. '''
        def mkFolder(path_):
            if not os.path.exists(path_):
                try: os.mkdir(path_)
                except WindowsError: FileError(3)

        folder_struct = self.prod_data['folders']
        main_folder   = os.path.join(self.prod_data['project'], self.project_name)

        mkFolder(main_folder)    
        for main, sub in folder_struct.iteritems():
            mkFolder(os.path.join(main_folder, main))
            for s in sub: 
                mkFolder(os.path.join(main_folder, main, s))

    def make_scene_ctrl(self):
        ''' Makes a scene control node. Consists of a null "__SCENE__" with an annotation tag 
        containing metadata for this object. '''
        doc = core.doc()
        doc.StartUndo()
        # create null
        scene_ctrl = c4d.BaseObject(c4d.Onull)
        doc.InsertObject(scene_ctrl)
        doc.AddUndo(c4d.UNDOTYPE_NEW, scene_ctrl)
        scene_ctrl.SetName('__SCENE__')
        # create and populate tag
        scene_tag  = core.tag(scene_ctrl, typ=c4d.Tannotation, name='SCENE_DATA')[0]
        annotation = "Production: {0}\nProject: {1}\nScene: {2}\nFramerate: {3}\nVersion: {4}"
        scene_tag[c4d.ANNOTATIONTAG_TEXT] = annotation.format(
            self.production, 
            self.proj_name, 
            self.scene_name,
            str(self.framerate), 
            str(self.version)
            )
        #        
        doc.AddUndo(c4d.UNDOTYPE_NEW, scene_tag)
        c4d.EventAdd()
        doc.EndUndo()

        return (scene_ctrl, scene_tag)

    # MISC. OPERATIONS 
    def save(self):
        ''' Saves and backs up the current scene file. '''
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
                raise status.FileError(2)

            incr_name = "{0}.{1}.{2}".format(name, str(cur_vers).zfill(4), ext)
            incr_file = os.path.join(file_path, incr_name)

            if os.path.exists(incr_file):
                incr_file = increment(incr_file)
            return incr_file
        #
        self.repath()

        backup_folder = os.path.join(self.file_folder, 'backup')
        backup_file  = os.path.join(backup_folder, self.file_name)
        backup_path  = increment(backup_file)

        if not os.path.exists(backup_folder):
            makedirs(backup_folder)
        if not os.path.exists(self.file_folder):
            makedirs(self.file_folder)

        try:
            core.saveAs(backup_path)
            core.saveAs(self.file_path)
        except status.FileError:
            raise status.FileError(0)

    def rename(self, name=None, verbose=True):
        ''' Rename the scene (with optional dialog) '''
        old_name = self.scene_name
        if (name == None):
            dlg = c4d.gui.RenameDialog(old_name)
            if (dlg==old_name) or (dlg==None) or (dlg==False):
                return
            else: name = dlg
        # store the old name and update self
        self.scene_name = name
        self.repath()
        # check that the new file doesn't already exist
        if os.path.isfile(self.file_path) and (verbose):
            msg = 'Warning: A scene with this name already exists -- proceed anyway? (Existing renders may be overwritten -- check your output version before rendering!)'
            prompt = c4d.gui.MessageDialog(msg, c4d.GEMB_OKCANCEL)
            if (prompt == c4d.GEMB_R_OK):
                pass
            elif (prompt == c4d.GEMB_R_CANCEL):
                # restore the old scene name and exit
                self.scene_name = old_name
                self.updateFilePath()
                return
        # set clean version, update scene_ctrl with new data, and save
        self.version = 1
        self.push_scene()
        self.push_output_paths()
        self.saveWithBackup()

    def version_up(self):
        ''' Version up the scene and save a new backup. '''
        if not self.isPipelined(): return False
        self.version += 1
        self.push_scene()
        self.push_output_paths()
        self.saveWithBackup()

    def sort(self):
        ''' Sorts objects into takes (via override groups) using sorting logic stored in a proj database.'''
        sort_dict = self.prod_data['sort']
        doc = core.doc()
        td  = doc.GetTakeData()
        # Parse the sorting dictionary into lists of objects
        for layer_, sort in sort_dict.iteritems():
            for tag_ in sort['rgb']:
                rgba_obj = [o.GetObject() for o in core.lsTags(name=tag_, typ=c4d.Tannotation) if not tag_=='']
            for tag_ in sort['pvo']:
                pvo_obj = [o.GetObject() for o in core.lsTags(name=tag_, typ=c4d.Tannotation) if not tag_=='']
            for tag_ in sort['occ']:
                occ_obj = [o.GetObject() for o in core.lsTags(name=tag_, typ=c4d.Tannotation) if not tag_=='']
            for tag_ in sort['off']:
                off_obj = [o.GetObject() for o in core.lsTags(name=tag_, typ=c4d.Tannotation) if not tag_=='']
            # Make the layer for sorting
            doc.StartUndo()
            layer = core.take(layer_, set_active=True)
            doc.AddUndo(c4d.UNDOTYPE_NEW, layer)
            start = layer.GetFirstOverrideGroup()
            # Add the sorted objects to their respective render layers / takes
            for og in core.ObjectIterator(start):
                if og.GetName() == 'bty':
                    pass
                    #for obj in rgba_obj:
                    #    doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj)
                    #    og.AddToGroup(td, obj)
                elif og.GetName() == 'pv_off':
                    for obj in pvo_obj:
                        doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj)
                        og.AddToGroup(td, obj)
                elif og.GetName() == 'black_hole':
                    for obj in occ_obj:
                        doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj)
                        og.AddToGroup(td, obj)
                elif og.GetName() == 'disable':
                    for obj in off_obj:
                        doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj)
                        og.AddToGroup(td, obj)
            doc.EndUndo()

def clearAllMultipasses():
    ''' Clears all multipass objects from the current RenderData '''
    doc = c4d.documents.GetActiveDocument()
    rdata = doc.GetActiveRenderData()
    doc.StartUndo()
    for mpass in core.ObjectIterator(rdata.GetFirstMultipass()):
        mpass.Remove()
    c4d.EventAdd()
    doc.EndUndo()
    return True

def clearObjectBuffers():
    ''' Clears all object buffers from the current RenderData '''
    doc = c4d.documents.GetActiveDocument()
    rdata = doc.GetActiveRenderData()
    doc.StartUndo()
    for mpass in core.ObjectIterator(rdata.GetFirstMultipass()):
        if (mpass.GetTypeName() == 'Object Buffer'):
            doc.AddUndo(c4d.UNDOTYPE_DELETE, mpass)
            mpass.Remove()
    c4d.EventAdd()
    doc.EndUndo()
    return True

def enableObjectBuffer(id):
    ''' Inserts an object buffer into the active render data, with the passed id'''
    doc = c4d.documents.GetActiveDocument()
    rd = doc.GetActiveRenderData()
    ob = c4d.BaseList2D(c4d.Zmultipass)
    ob.GetDataInstance()[c4d.MULTIPASSOBJECT_TYPE] = c4d.VPBUFFER_OBJECTBUFFER
    ob[c4d.MULTIPASSOBJECT_OBJECTBUFFER] = id
    rd.InsertMultipass(ob)
    c4d.EventAdd()

def createObjectBuffers(consider_takes=False):
    ''' Parses the scene for all compositing tags with object buffers enabled, then creates them.'''    
    doc = c4d.documents.GetActiveDocument()
    td = doc.GetTakeData()
    # clear all existing object buffers
    self.clearObjectBuffers()
    # "simple" mode -- takes are not considered, existing render data is modified
    if not (consider_takes):
        self._buildObjectBuffers()
    # "complicated" mode -- creates child RenderData for each take, enabling only object buffers
    # belonging to visible objects in the take
    elif (consider_takes):
        # Operates only on "checked" takes -- those flagged in the scene
        take_list = core.getCheckedTakes()
        # if no takes are checked, escape
        if len(take_list) == 0:
            return
        # Get the active render data -- this will be the primary RenderData from which the chilrden
        # will inherit
        parent_rdata = doc.GetActiveRenderData()
        if parent_rdata.GetUp():
            raise status.PipelineError(4)
            return
        # Create a child renderdata for each take
        for take in take_list:
            # Change the take -- this will affect all the necessary visibility flags
            td.SetCurrentTake(take)
            # Create the child data
            child_rdata = core.createChildRenderData(parent_rdata, suffix=take.GetName(), set_active=True)
            # Set up Object Buffers for the objects visible in the current take
            self._buildObjectBuffers()
            # Assign the RenderData to the take
            take.SetRenderData(td, child_rdata)
            c4d.EventAdd()

def createUtilityPass(take=None):
    ''' Creates a utility pass version of the passed take. If no take is passed, it will create one
        for the main take.'''
    doc = c4d.documents.GetActiveDocument()
    td  = doc.GetTakeData()
    parent_rdata = doc.GetActiveRenderData()
    # use the main take if none is passed
    if (take == None):
        take = td.GetMainTake()

    # make the take active and create a child render data to attach to it
    new_take = core.take('{}_util'.format(take.GetName()), set_active=True)
    child_rdata = core.createChildRenderData(parent_rdata, suffix='UTIL', set_active=True)
    new_take.SetRenderData(td, child_rdata)
    self.clearAllMultipasses()

    # modify renderdata for 32-bit exr w/ data passes
    render_data = database.getProduction('DEFAULT')

    for multipass_id in render_data['passes_util']:
        mp_obj = c4d.BaseList2D(c4d.Zmultipass)
        mp_obj.GetDataInstance()[c4d.MULTIPASSOBJECT_TYPE] = eval(multipass_id)
        child_rdata.InsertMultipass(mp_obj)
    for attribute in render_data['image_settings_util']:
        child_rdata[eval(attribute)] = render_data['image_settings_util'][attribute]

    return (take, child_rdata)


def _getObjectBufferIDs():
    ''' Private. Gets a set of all unique Object Buffer ids set in compositing tags in the scene. '''
    ids = []
    channel_enable = 'c4d.COMPOSITINGTAG_ENABLECHN{}'
    channel_id     = 'c4d.COMPOSITINGTAG_IDCHN{}'
    doc = c4d.documents.GetActiveDocument()
    td = doc.GetTakeData()

    for obj in core.ObjectIterator(doc.GetFirstObject()):
        if core.isVisible(obj):
            for tag in core.TagIterator(obj):
                if tag.GetType() == c4d.Tcompositing:
                    for i in range(12):
                        if tag[eval(channel_enable.format(i))] == 1:
                            id_ = tag[eval(channel_id.format(i))]
                            ids.append(id_)
    return sorted(list(set(ids)), reverse=True)

def _buildObjectBuffers():
    ''' Private. '''
    # Get the object buffer IDs assigned to compositing tags in the scene
    # this operation also checks for objects that are invisible (dots) or flagged as matted  |
    # invisible to camera, and ignores them.
    ids = self._getObjectBufferIDs()
    for id_ in ids:
        # enable the passed object buffers 
        self.enableObjectBuffer(id_)

