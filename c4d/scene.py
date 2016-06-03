# !/usr/bin/python
# coding: UTF-8

#    Scene wrapper for Cinema 4d Python API
#    
#    Author:  Mark Rohrer
#    Contact: mark.rohrer@gmail.com
#    Version: 0.4
#    Date:    05/05/2016
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
from pipeline.c4d import core
from pipeline.c4d import database
from pipeline.c4d import error

reload(core)
reload(database)
reload(error)

class Scene(object):
    def __init__(self, delay=False):
        self.project_name = ''
        self.scene_name   = ''
        self.production   = ''
        self.file_path    = ''
        self.framerate    = 0
        self.version      = 0

        self.scene_ctrl, self.scene_tag, self.status = self.getSceneStatus()

        if (self.status == error.SCENE_OK):
            self.getSceneData()
            self.getProductionData()
            self.updateFilePath()
        elif (self.status == error.SCENE_BROKEN):
            raise error.PipelineError(self.status)
        elif (self.status == error.SCENE_NEW) and (delay):
            raise error.PipelineError(self.status)
        elif (self.status == error.SCENE_NEW):
            raise error.PipelineError(self.status)

    # GETTERS
    @classmethod
    def getSceneStatus(self):
        ''' Gets the status of the scene and returns any valid pipeline control objects.'''
        # Tuple to store scene_ctrl node, scene_tag node, and status message
        _status = (None, None, None)
        scene_ctrl = core.ls(name='__SCENE__')
        # No scene_ctrl found -- must be new scene
        if (scene_ctrl == None or scene_ctrl == []):
            _status = (None, None, error.SCENE_NEW)
        # One scene_ctrl found -- check it for a tag
        elif (len(scene_ctrl)==1):
            scene_ctrl = scene_ctrl[0]
            scene_tag  = core.lsTags(name='SCENE_DATA', typ=c4d.Tannotation, obj=scene_ctrl)
            # tag found -- status is green
            if (scene_tag):
                _status = (scene_ctrl, scene_tag[0], error.SCENE_OK)
            # no tag found on scene_ctrl -- scene is broken
            else:
                _status = (scene_ctrl, None, error.SCENE_BROKEN)
        # 2+ scene_ctrl found -- scene is broken
        elif (len(scene_ctrl)>1):
            _status = (None, None, error.SCENE_BROKEN)
        return _status

    @classmethod
    def isPipelined(self):
        if (self.getSceneStatus()[2] == error.SCENE_OK):
            return True
        else: return False

    def getSceneData(self):
        ''' Parses the data from the scene_ctrl tag into attributes for the scene and production.'''
        def _annoToDict(tag_data):
            ''' Takes a block of text from an annotation tag field and converts it to a dictionary.'''
            a = tag_data.split('\n')
            b = {}
            for a_ in a:
                kv = a_.split(':')
                b[kv[0]] = kv[1].lstrip()
            return b

        scene_data = _annoToDict(self.scene_tag[c4d.ANNOTATIONTAG_TEXT])

        self.production   = scene_data['Production']
        self.project_name = scene_data['Project']
        self.scene_name   = scene_data['Scene']
        self.framerate    = int(scene_data['Framerate'])
        self.version      = int(scene_data['Version'])

    def getProductionData(self):
        ''' Attaches the production database dictionary to the scene object. '''
        self.prod_data = database.getProduction(self.production)

    def getRenderVersion(self):
        ''' Placeholder until needed.'''
        pass

    def updateFilePath(self):
        self.file_name     = '{0}_{1}.c4d'.format(self.project_name, self.scene_name)
        self.file_folder   = os.path.join(self.prod_data['project'], self.project_name, 'c4d')
        self.backup_folder = os.path.join(self.file_folder, 'backup')
        self.file_path     = os.path.join(self.file_folder, self.file_name)

        return (self.file_name, self.file_folder, self.backup_folder, self.file_path)

    # SETTERS
    def setSceneData(self):
        ''' Does the opposite of getSceneData() '''
        def _sceneToAnno():
            out_str = ''
            out_str += 'Production: {0}\n'.format(self.production)
            out_str += 'Project: {0}\n'.format(self.project_name)
            out_str += 'Scene: {0}\n'.format(self.scene_name)
            out_str += 'Framerate: {0}\n'.format(self.framerate)
            out_str += 'Version: {0}'.format(self.version)
            return out_str
        #
        scene_ctrl, scene_tag, status = self.getSceneStatus()
        if (status == error.SCENE_OK):
            self.scene_tag[c4d.ANNOTATIONTAG_TEXT] = _sceneToAnno()
            return True
        else:
            return False

    def setOutput(self, set_=True, paths_only=False):
        ''' Set render output settings (based on production) '''
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
        if (set_):
            setOutput(
                default_override=False,
                paths_only  = paths_only,
                prod        = self.production,
                frate       = self.framerate,
                version     = self.version,
                output_path = self.output_path,
                multi_path  = self.multi_path
                )

    def setTakes(self):
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
        self.updateFilePath()
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
        self.setSceneData()
        self.setOutput()
        self.saveWithBackup()

    def versionUp(self):
        ''' Version up the scene and save a new backup. '''
        if not self.isPipelined(): return False
        self.version += 1
        self.setSceneData()
        self.setOutput(paths_only=True)
        self.saveWithBackup()

    # BUILDERS / OPERATIONS
    def makeFolders(self, check_project=False):
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

    @classmethod        
    def clearObjectBuffers(self):
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

    @classmethod
    def getObjectBufferIDs(self):
        ''' Gets a set of all unique Object Buffer ids set in compositing tags in the scene. '''
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

    @classmethod
    def enableObjectBuffer(self, id):
        '''Inserts an object buffer into the active render data, with the passed id'''
        doc = c4d.documents.GetActiveDocument()
        rd = doc.GetActiveRenderData()
        ob = c4d.BaseList2D(c4d.Zmultipass)
        ob.GetDataInstance()[c4d.MULTIPASSOBJECT_TYPE] = c4d.VPBUFFER_OBJECTBUFFER
        ob[c4d.MULTIPASSOBJECT_OBJECTBUFFER] = id
        rd.InsertMultipass(ob)
        c4d.EventAdd()

    @classmethod    
    def createObjectBuffers(self, consider_takes=False):
        '''Parses the scene for all compositing tags with object buffers enabled, then creates them'''
        def _build():
            # Get the object buffer IDs assigned to compositing tags in the scene
            # this operation also checks for objects that are invisible (dots) or flagged as matted  |
            # invisible to camera, and ignores them.
            ids = self.getObjectBufferIDs()
            for id_ in ids:
                # enable the passed object buffers 
                self.enableObjectBuffer(id_)
    
        doc = c4d.documents.GetActiveDocument()
        td = doc.GetTakeData()
        # clear all existing object buffers
        self.clearObjectBuffers()
        # "simple" mode -- takes are not considered, existing render data is modified
        if not (consider_takes):
            self._build()
        # "complicated" mode -- creates child RenderData for each take, enabling only object buffers
        # belonging to visible objects in the take
        elif (consider_takes):
            # Operates only on "checked" takes -- those flagged in the scene
            take_list = self.getCheckedTakes()
            # if no takes are checked, escape
            if len(take_list) == 0:
                return
            # Get the active render data -- this will be the primary RenderData from which the chilrden
            # will inherit
            parent_rdata = doc.GetActiveRenderData()
            # Create a child renderdata for each take
            for take in take_list:
                # Change the take -- this will affect all the necessary visibility flags
                td.SetCurrentTake(take)
                # Create the child data
                child_rdata = self.createChildRenderData(parent_rdata, suffix=take.GetName(), set_active=True)
                # Set up Object Buffers for the objects visible in the current take
                self._build_()
                # Assign the RenderData to the take
                take.SetRenderData(td, child_rdata)
                c4d.EventAdd()
   
    @classmethod
    def makeSceneCtrl(self):
        ''' Makes a scene control node -- a null called '__SCENE__' '''
        doc = core.doc()
        doc.StartUndo()
        scene_ctrl = c4d.BaseObject(c4d.Onull)
        doc.InsertObject(scene_ctrl)
        doc.AddUndo(c4d.UNDOTYPE_NEW, scene_ctrl)
        scene_ctrl.SetName('__SCENE__')
        scene_tag = core.tag(scene_ctrl, typ=c4d.Tannotation, name='SCENE_DATA')[0]
        doc.AddUndo(c4d.UNDOTYPE_NEW, scene_tag)
        c4d.EventAdd()
        doc.EndUndo()
        return (scene_ctrl, scene_tag)

    def saveWithBackup(self):
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
                raise error.FileError(2)

            incr_name = "{0}.{1}.{2}".format(name, str(cur_vers).zfill(4), ext)
            incr_file = os.path.join(file_path, incr_name)

            if os.path.exists(incr_file):
                incr_file = increment(incr_file)
            return incr_file
        #
        self.updateFilePath()

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
        except error.FileError:
            raise error.FileError(0)

    def sortTakes(self):
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

def setOutput( default_override=True, paths_only=False, prod='DEFAULT', **scene_data ):
    ''' Sets up basic parameters for rendering. Specifics are pulled from 'project' global 
    parameters module.

    scene_data: data unique to the scene being set up (paths, version, etc)
    render_data: production-specific data (raytracing globals, resolution, etc). '''
    doc = core.doc()
    if (paths_only):
        rd = doc.GetActiveRenderData()
    else:
        rd = c4d.documents.RenderData()

    # OUTPUT PATHS
    # default_override will set default raytracing & resolution settings, but has no information
    # on which to base output paths.  Therefore it will leave them blank.
    if (default_override):
        render_data = database.getProduction('DEFAULT')
        render_data['output_path'] = ''
        render_data['multi_path'] = ''
    else:
        render_data = database.getProduction(prod)
    # Set the values
    rd[c4d.RDATA_PATH] = str(scene_data['output_path'])
    if not (scene_data['output_path'] == ''):
        rd[c4d.RDATA_MULTIPASS_FILENAME] = str(scene_data['multi_path'])
    # The 'paths_only' flag is for the Version Up utility, so that any custom render settings are
    # not reset by versioning up.  this branch will return immediately after setting output paths
    if (paths_only): return True

    # STANDARD OUTPUT SETTINGS
    # Resolution / naming convention / bit depth & channels
    rd[c4d.RDATA_FRAMERATE] = int(scene_data['frate'])
    for attribute in render_data['output']:
        rd[eval(attribute)] = render_data['output'][attribute]

    # SAMPLER SETTINGS --
    # Universal(?) settings
    # AA Sampling overrides
    for attribute in render_data['standard']:
        rd[eval(attribute)] = render_data['standard'][attribute]

    # RENDERER-SPECIFIC SETTINGS
    # Standard renderer -- >
    if (render_data['renderer'] == c4d.RDATA_RENDERENGINE_STANDARD):
        rd[c4d.RDATA_RENDERENGINE] = c4d.RDATA_RENDERENGINE_STANDARD

    # Physical renderer -- >
    elif (render_data['renderer'] == c4d.RDATA_RENDERENGINE_PHYSICAL):
        rd[c4d.RDATA_RENDERENGINE] = c4d.RDATA_RENDERENGINE_PHYSICAL
        vpost = rd.GetFirstVideoPost()
        # Check for existing Physical renderer effect
        while vpost:
            if vpost.CheckType(c4d.VPxmbsampler): break
            vpost = vpost.GetNext()
        # Make one if it doesn't exist
        if not vpost:
            vpost = c4d.BaseList2D(c4d.VPxmbsampler)
            rd.InsertVideoPost(vpost)
        # Set the attrs from the DB
        for attribute in render_data['physical']:
            vpost[eval(attribute)] = render_data['physical'][attribute]

    # MULTI-PASS TOGGLES
    for multipass_id in render_data['passes']:
        mp_obj = c4d.BaseList2D(c4d.Zmultipass)
        mp_obj.GetDataInstance()[c4d.MULTIPASSOBJECT_TYPE] = eval(multipass_id)
        rd.InsertMultipass(mp_obj)

    # ADDITIONAL VIDEO POST EFFECTS
    if 'effects' in render_data:
        for effect_id in render_data['effects']:
            vpost = c4d.BaseList2D(eval(effect_id))
            rd.InsertVideoPost(vpost)
            for attribute in render_data['effects'][effect_id]:
                vpost[eval(attribute)] = render_data['effects'][effect_id][attribute]

    core.createRenderData(rd, 'My Render Setting')

    c4d.EventAdd()

    return
