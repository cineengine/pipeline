# !/usr/bin/python
# coding: UTF-8

#    Scene wrapper for Cinema 4d Python API
#    
#    Author:  Mark Rohrer
#    Contact: mark.rohrer@gmail.com
#    Version: 0.2
#    Date:    03/18/2016
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


# OPERATIONS ######################################################################################
# Each of these operations is dependent on a scene_data object, which is a dictionary parsed from a
# __SCENE__ node's annotation tag.  In other words, these are pipeline-specific operations, and 
# (with few exceptions) cannot be run outside of that context
def saveWithBackup(scene_data):
    ''' Backs up the current scene file. '''
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

        incr_name = "{}.{}.{}".format(name, str(cur_vers).zfill(4), ext)
        incr_file = os.path.join(file_path, incr_name)

        if os.path.exists(incr_file):
            incr_file = increment(incr_file)
        return incr_file
    #   
    prod_data   = getProductionData(scene_data)
    scene_path  = os.path.join(prod_data['project'], scene_data['Project'], 'c4d')
    scene_name  = '{}_{}.c4d'.format(scene_data['Project'], scene_data['Scene'])
    scene_file  = os.path.join(scene_path, scene_name)

    backup_path = os.path.join(scene_path, 'backup')
    backup_file = os.path.join(backup_path, scene_name)
    backup_file = increment(backup_file)

    if not os.path.exists(backup_path):
        makedirs(backup_path)
    if not os.path.exists(scene_path):
        makedirs(scene_path)

    try:
        core.saveAs(backup_file)
        core.saveAs(scene_file)
    except error.FileError:
        raise error.FileError(0)

    return


def makeFolders(scene_data):
    ''' Makes folders for a new project. '''
    def mkFolder(path_):
        if not os.path.exists(path_):
            try: os.mkdir(path_)
            except WindowsError: FileError(3)

    prod_data     = getProductionData(scene_data)
    folder_struct = prod_data['folders']
    main_folder   = os.path.join(prod_data['project'], scene_data['Project'])

    mkFolder(main_folder)    
    for main, sub in folder_struct.iteritems():
        mkFolder(os.path.join(main_folder, main))
        for s in sub: 
            mkFolder(os.path.join(main_folder, main, s))


# INITIALIZERS ####################################################################################
def init(set_output=False, make_folders=False, save=False):
    ''' Initializes a scene for pipeline operations. It will either parse existing scene data,
    or prompt the user to create a new scene. Optional flags available to set render output,
    make project folders, and force a save & backup of the scene.'''
    # Check the scene's current status
    scene_ctrl, scene_tag = getSceneCtrl()
    # No control nodes exist (make one via user query)
    if not (scene_ctrl):
        dlg = ProjectInitWindow()
        if dlg.Open(c4d.DLG_TYPE_MODAL, defaultw=300, defaulth=50):
            pass
        else: return
    # parse scene data
    scene_data = getSceneData()
    # get production dictionary
    prod_data = getProductionData(scene_data)
    # create necessary folders
    if make_folders:
        makeFolders(scene_data)
    # set output settings for show / project
    if set_output:
        setOutput(scene_data)
    # save scene
    if save:
        saveWithBackup(scene_data)

    return scene_data


def getSceneData():
    ''' Gets the scene controller and parses its annotation tag into a dictionary.'''
    scene_ctrl, scene_tag = getSceneCtrl()
    if (scene_ctrl == None) or (scene_tag == None):
        raise error.PipelineError(0)
    scene_data = annoToDict(scene_tag[c4d.ANNOTATIONTAG_TEXT])
    return scene_data


def annoToDict(tag_data):
    ''' Takes a block of text from an annotation tag field and converts it to a dictionary.'''
    a = tag_data.split('\n')
    b = {}
    for a_ in a:
        kv = a_.split(':')
        b[kv[0]] = kv[1].lstrip()
    return b


def getSceneCtrl():
    ''' Gets the scene controller and its annotation tag from the current scene. '''
    scene_ctrl = core.ls(name='__SCENE__')
    if (scene_ctrl == None or scene_ctrl == []):
        return (None, None)
    elif (len(scene_ctrl)==1):
        scene_ctrl = scene_ctrl[0]
        scene_tag = core.lsTags(name='SCENE_DATA', typ=c4d.Tannotation, obj=scene_ctrl)[0]
        if scene_tag == None:
            return (None, None)
        else:
            return (scene_ctrl, scene_tag)
    elif (len(scene_ctrl)>1):
        raise PipelineError(1)


def getProductionData(scene_data):
    ''' Retrieves production database based on scene data. '''
    #prod_data = database.PRODUCTIONS[scene_data['Production']]
    prod_data = database.getProduction(scene_data['Production'])
    return prod_data


# RENDERING #######################################################################################
def setOutput( scene_data=None ):
    ''' A generic (non-pipeline-specific) function that sets up basic parameters for rendering. 
    Specifics are pulled from 'project' global parameters module.'''
    if (scene_data == None):
        output_path = ''
        prod_data   = database.getProduction('DEFAULT')
    else:
        prod_data = getProductionData(scene_data)
        prod_data['frate'] = scene_data['Framerate']
        output_path = os.path.join(
            prod_data['project'],
            scene_data['Project'],
            'render_3d',
            scene_data['Scene'],
            'v{}'.format(scene_data['Version'].zfill(3)),
            '$take',
            '{}_{}'.format(scene_data['Scene'], '$take')
            )
        multi_path = os.path.join(
            prod_data['project'],
            scene_data['Project'],
            'render_3d',
            scene_data['Scene'],
            'v{}'.format(scene_data['Version'].zfill(3)),
            '$take_passes',
            '{}_{}'.format(scene_data['Scene'], '$take')
            )

    res    = (prod_data['xres'], prod_data['yres'])
    frate  = int(prod_data['frate'])
    aspect = 1.7777

    doc    = core.doc()
    rd     = c4d.documents.RenderData()

    # GLOBAL SETTINGS
    doc.SetFps(frate)
    # Output paths
    rd[c4d.RDATA_PATH]            = output_path
    # Resolution & frame rate
    rd[c4d.RDATA_XRES]            = res[0]
    rd[c4d.RDATA_YRES]            = res[1]
    rd[c4d.RDATA_LOCKRATIO]       = True
    rd[c4d.RDATA_FILMASPECT]      = aspect
    rd[c4d.RDATA_FILMPRESET]      = c4d.RDATA_FILMPRESET_HDTV
    rd[c4d.RDATA_FRAMERATE]       = float(frate)
    # Alpha channel
    rd[c4d.RDATA_ALPHACHANNEL]    = True
    rd[c4d.RDATA_SEPARATEALPHA]   = False
    rd[c4d.RDATA_STRAIGHTALPHA]   = True
    # Format options    
    rd[c4d.RDATA_FORMAT]          = c4d.FILTER_PNG
    rd[c4d.RDATA_FORMATDEPTH]     = c4d.RDATA_FORMATDEPTH_16
    # Frame padding & extension
    rd[c4d.RDATA_NAMEFORMAT]      = c4d.RDATA_NAMEFORMAT_6    
    # AA Sampling overrides
    rd[c4d.RDATA_ANTIALIASING]    = c4d.RDATA_ANTIALIASING_BEST
    rd[c4d.RDATA_AAFILTER]        = c4d.RDATA_AAFILTER_ANIMATION
    rd[c4d.RDATA_AAMINLEVEL]      = c4d.RDATA_AAMINLEVEL_2
    rd[c4d.RDATA_AAMAXLEVEL]      = c4d.RDATA_AAMAXLEVEL_8

    # MULTIPASS
    # Output paths
    if not (output_path == ''):
        rd[c4d.RDATA_MULTIPASS_FILENAME] = multi_path
    # Format options
    rd[c4d.RDATA_MULTIPASS_SAVEFORMAT] = c4d.FILTER_PNG
    rd[c4d.RDATA_MULTIPASS_SAVEDEPTH]  = c4d.RDATA_FORMATDEPTH_16
    # Raytracing overrides
    rd[c4d.RDATA_RAYDEPTH]        = 5
    rd[c4d.RDATA_REFLECTIONDEPTH] = 2
    rd[c4d.RDATA_SHADOWDEPTH]     = 2
    # Miscellaneous
    rd[c4d.RDATA_TEXTUREERROR]    = True

    for mp in prod_data['passes']:
        mp_obj = c4d.BaseList2D(c4d.Zmultipass)
        mp_obj.GetDataInstance()[c4d.MULTIPASSOBJECT_TYPE] = mp
        rd.InsertMultipass(mp_obj)

    core.createRenderData(rd, 'DEFAULT')
    return


def setTakes(scene_data):
    ''' Makes the default takes (render layers) and overrides for the specified project. '''
    prod_data = getProductionData(scene_data)
    td        = core.doc().GetTakeData()
    for take_ in prod_data['layers']:
        take = core.take(take_, set_active=True)
        take.SetChecked(True)
        # Add the default override groups to the take
        for og_ in core.OVERRIDE_GROUPS:
            og = core.override(take, og_)
            # Add the compositing tag for overriding
            tag = og.AddTag(td, c4d.Tcompositing, mat=None)
            tag.SetName('VISIBILITY_OVERRIDE')
            # ... and set the default values
            setCompositingTag( tag, og_ )
    return


def sortTakes(scene_data):
    ''' Sorts objects into takes (via override groups) using sorting logic stored in a proj database.'''
    prod_data = getProductionData(scene_data)
    sort_dict = prod_data['sort']
    td = core.doc().GetTakeData()
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
        layer = core.take(layer_, set_active=True)
        start = layer.GetFirstOverrideGroup()
        # Add the sorted objects to their respective render layers / takes
        for og in core.ObjectIterator(start):
            if og.GetName() == 'bty':
                for obj in rgba_obj:
                    og.AddToGroup(td, obj)
            elif og.GetName() == 'pv_off':
                for obj in pvo_obj:
                    og.AddToGroup(td, obj)
            elif og.GetName() == 'black_hole':
                for obj in occ_obj:
                    og.AddToGroup(td, obj)
            elif og.GetName() == 'disable':
                for obj in off_obj:
                    og.AddToGroup(td, obj)


# UI OBJECTS ######################################################################################
class ProjectInitWindow(gui.GeDialog):
    def __init__(self):
        self.LBL_SHOW_NAME    = 1000
        self.LBL_PROJECT_NAME = 1001
        self.LBL_SCENE_NAME   = 1002
        self.LBL_FRAMERATE    = 1003
        self.LBL_PREVIEW_DIR  = 1004
        self.LBL_PREVIEW_SCN  = 1005

        self.TXT_PROJECT_NAME = 2001
        self.TXT_SCENE_NAME   = 2002
        self.TXT_PREVIEW_DIR  = 2004
        self.TXT_PREVIEW_SCN  = 2005

        self.DRP_SHOW_NAME    = 3000
        self.RDO_FRAMERATE    = 3003
        self.RDO_FRAMERATE_T  = 3030
        self.RDO_FRAMERATE_S  = 3060
        self.BTN_EXECUTE      = 3009
        self.BTN_CANCEL       = 3010

        self.GROUP_MAIN       = 9000
        self.GROUP_BTNS       = 9001

        self.PRODUCTION_ID    = {}
        self.PRODUCTION_ITR   = 10000
        for proj in database.getAllProductions():
            self.PRODUCTION_ID[self.PRODUCTION_ITR] = proj
            self.PRODUCTION_ITR += 1


    def CreateLayout(self):
        # Headers
        self.SetTitle('Create New Project')        
        self.GroupBegin(self.GROUP_MAIN, c4d.BFH_LEFT, 2, 1)
        # Show selection dropdown
        self.AddStaticText(self.LBL_SHOW_NAME, c4d.BFH_LEFT, name='Select Production:')
        self.AddComboBox(self.DRP_SHOW_NAME, c4d.BFH_LEFT, 600)
        for proj in self.PRODUCTION_ID:
            self.AddChild(self.DRP_SHOW_NAME, proj, self.PRODUCTION_ID[proj])
        # Project text field
        self.AddStaticText(self.LBL_PROJECT_NAME, c4d.BFH_LEFT, name='Project Name:')
        self.AddEditText(self.TXT_PROJECT_NAME, c4d.BFH_LEFT, 600)
        # Scene text field
        self.AddStaticText(self.LBL_SCENE_NAME, c4d.BFH_LEFT, name='Scene Tag:')
        self.AddEditText(self.TXT_SCENE_NAME, c4d.BFH_LEFT, 200)
        # Framerate radio button
        self.AddStaticText(self.LBL_FRAMERATE, c4d.BFH_LEFT, name='Framerate:')
        self.AddRadioGroup(self.RDO_FRAMERATE, c4d.BFH_LEFT, rows=2)
        self.AddChild(self.RDO_FRAMERATE, self.RDO_FRAMERATE_T, '30 fps')
        self.AddChild(self.RDO_FRAMERATE, self.RDO_FRAMERATE_S, '60 fps')
        # Preview area
        self.AddStaticText(self.LBL_PREVIEW_SCN, c4d.BFH_LEFT, name='Scene Name:')
        self.AddEditText(self.TXT_PREVIEW_SCN, c4d.BFH_LEFT, 600)
        self.Enable(self.TXT_PREVIEW_SCN, 0)
        self.AddStaticText(self.LBL_PREVIEW_DIR, c4d.BFH_LEFT, name='Proj Folder:')
        self.AddEditText(self.TXT_PREVIEW_DIR, c4d.BFH_LEFT, 600)
        self.Enable(self.TXT_PREVIEW_DIR, 0)
        self.GroupEnd()
        # Execute btn
        self.GroupBegin(self.GROUP_BTNS, c4d.BFH_RIGHT, 2, 1)
        self.AddButton(self.BTN_EXECUTE, c4d.BFH_SCALE, name='Create Project')
        self.AddButton(self.BTN_CANCEL, c4d.BFH_SCALE, name='Cancel')
        # Footers
        self.GroupEnd()
        self.ok = False
        return True


    def Command(self, id, msg):
        if id == self.BTN_EXECUTE:
            self.ok = True
            self.execute()
            self.Close()
        elif id == self.BTN_CANCEL:
            self.Close()
        elif (id == self.TXT_PROJECT_NAME or
              id == self.TXT_SCENE_NAME or
              id == self.DRP_SHOW_NAME):
            self.preview()
        return True


    @classmethod
    def makeSceneCtrl(self):
        ''' Makes a scene control node -- a null called '__SCENE__' '''
        doc = core.doc()
        scene_ctrl = c4d.BaseObject(c4d.Onull)
        doc.InsertObject(scene_ctrl)
        scene_ctrl.SetName('__SCENE__')
        scene_tag = core.tag(scene_ctrl, typ=c4d.Tannotation, name='SCENE_DATA')[0]
        c4d.EventAdd()
        return (scene_ctrl, scene_tag)


    def execute(self):
        show_name  = self.PRODUCTION_ID[self.GetInt32(self.DRP_SHOW_NAME)]
        proj_name  = self.GetString(self.TXT_PROJECT_NAME)
        scene_name = self.GetString(self.TXT_SCENE_NAME)
        framerate  = self.GetInt32(self.RDO_FRAMERATE)-3000

        scene_ctrl, tag   = self.makeSceneCtrl()
        annotation        = "Production: {}\nProject: {}\nScene: {}\nFramerate: {}\nVersion: {}"
        annotation        = annotation.format(show_name, proj_name, scene_name, str(framerate), str(1))
        tag[c4d.ANNOTATIONTAG_TEXT] = annotation

        scene_data = getSceneData()
        makeFolders(scene_data)
        setOutput(scene_data)
        saveWithBackup(scene_data)
        return True


    def preview(self):
        show_name  = self.PRODUCTION_ID[self.GetInt32(self.DRP_SHOW_NAME)]
        proj_name  = self.GetString(self.TXT_PROJECT_NAME)
        scene_name = self.GetString(self.TXT_SCENE_NAME)
        prod_data  = database.getProduction(show_name)['project']

        proj_name  = proj_name.replace(' ', '_')
        scene_name = scene_name.replace(' ', '_')
        self.SetString(self.TXT_PROJECT_NAME, proj_name)
        self.SetString(self.TXT_SCENE_NAME, scene_name)

        scene_prev = '{}_{}.c4d'.format(proj_name, scene_name)
        proj_prev  = os.path.relpath(
            "{}\\{}\\c4d\\".format(prod_data, proj_name),
            "\\\\cagenas\\workspace\\MASTER_PROJECTS\\"            
            )

        self.SetString(self.TXT_PREVIEW_DIR, proj_prev)
        self.SetString(self.TXT_PREVIEW_SCN, scene_prev)
        return True