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

reload(core)
reload(database)
reload(error)


class Scene(object):
    def __init__(self, delay=False):
        self.project_name = ''
        self.scene_name   = ''
        self.production   = ''
        self.framerate    = 0
        self.version      = 0

        self.scene_ctrl, self.scene_tag, self.status = self.getSceneStatus()

        if (self.status == error.SCENE_OK):
            self.getSceneData()
            self.getProductionData()
        elif (self.status == error.SCENE_BROKEN):
            raise error.PipelineError(status)
        elif (self.status == error.SCENE_NEW) and (delay):
            raise error.PipelineError(status)
        elif (self.status == error.SCENE_NEW):
            dlg = ProjectInitWindow()
            dlg.Open(c4d.DLG_TYPE_MODAL, defaultw=300, defaulth=50)


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
            scene_tag  = core.lsTags(name='SCENE_DATA', typ=c4d.Tannotation, obj=scene_ctrl)[0]
            # tag found -- status is green
            if (scene_tag):
                _status = (scene_ctrl, scene_tag, error.SCENE_OK)
            # no tag found on scene_ctrl -- scene is broken
            else:
                _status = (scene_ctrl, None, error.SCENE_BROKEN)
        # 2+ scene_ctrl found -- scene is broken
        elif (len(scene_ctrl)>1):
            _status = (None, None, error.SCENE_BROKEN)
        return _status


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


    def setSceneData(self):
        ''' Does the opposite of getSceneData() '''
        def _sceneToAnno():
            out_str = ''
            out_str += 'Production: {}\n'.format(self.production)
            out_str += 'Project: {}\n'.format(self.project_name)
            out_str += 'Scene: {}\n'.format(self.scene_name)
            out_str += 'Framerate: {}\n'.format(self.framerate)
            out_str += 'Version: {}'.format(self.version)
            return out_str
        #
        scene_ctrl, scene_tag, status = self.getSceneStatus()
        if (status == error.SCENE_OK):
            self.scene_tag[c4d.ANNOTATIONTAG_TEXT] = _sceneToAnno()
            return True
        else:
            return False


    def getProductionData(self):
        ''' Attaches the production database dictionary to the scene object. '''
        self.prod_data = database.getProduction(self.production)


    def makeFolders(self):
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
    def makeSceneCtrl(self):
        ''' Makes a scene control node -- a null called '__SCENE__' '''
        doc = core.doc()
        scene_ctrl = c4d.BaseObject(c4d.Onull)
        doc.InsertObject(scene_ctrl)
        scene_ctrl.SetName('__SCENE__')
        scene_tag = core.tag(scene_ctrl, typ=c4d.Tannotation, name='SCENE_DATA')[0]
        c4d.EventAdd()
        return (scene_ctrl, scene_tag)


    def setOutput(self):
        ''' Set render output settings (based on production) '''
        output_path = os.path.join(
            self.prod_data['project'],
            self.project_name,
            'render_3d',
            self.scene_name,
            'v{}'.format(str(self.version).zfill(3)),
            '$take',
            '{}_{}'.format(self.scene_name, '$take')
            )
        multi_path = os.path.join(
            self.prod_data['project'],
            self.project_name,
            'render_3d',
            self.scene_name,
            'v{}'.format(str(self.version).zfill(3)),
            '$take_passes',
            '{}_{}'.format(self.scene_name, '$take')
            )
        setOutput(
            default_override=False,
            xres        = self.prod_data['xres'],
            yres        = self.prod_data['yres'],
            frate       = self.prod_data['frate'],
            passes      = self.prod_data['passes'],
            version     = self.version,
            output_path = output_path,
            multi_path  = multi_path
            )


    def rename(self, name=None):
        ''' Rename the scene (with optional dialog) '''
        if (name == None):
            dlg = c4d.gui.RenameDialog('New scene name')
            if (dlg==False):
                return
            else: name = dlg

        self.scene_name = name
        self.version = 1
        self.setSceneData()
        self.saveWithBackup()


    def versionUp(self):
        ''' Version up the scene and save a new backup. '''
        self.version += 1
        self.setSceneData()
        self.saveWithBackup()


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

            incr_name = "{}.{}.{}".format(name, str(cur_vers).zfill(4), ext)
            incr_file = os.path.join(file_path, incr_name)

            if os.path.exists(incr_file):
                incr_file = increment(incr_file)
            return incr_file
        #   
        prod_data   = self.prod_data
        scene_path  = os.path.join(prod_data['project'], self.project_name, 'c4d')
        scene_name  = '{}_{}.c4d'.format(self.project_name, self.scene_name)
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


    def setTakes(self):
        ''' Makes the default takes (render layers) and overrides for the specified production. '''
        td = core.doc().GetTakeData()
        for take_ in self.prod_data['layers']:
            take = core.take(take_, set_active=True)
            take.SetChecked(True)
            # Add the default override groups to the take
            for og_ in core.OVERRIDE_GROUPS:
                og = core.override(take, og_)
                # Add the compositing tag for overriding
                tag = og.AddTag(td, c4d.Tcompositing, mat=None)
                tag.SetName('VISIBILITY_OVERRIDE')
                # ... and set the default values
                core.setCompositingTag( tag, og_ )
        return


    def sortTakes(self):
        ''' Sorts objects into takes (via override groups) using sorting logic stored in a proj database.'''
        sort_dict = self.prod_data['sort']
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


def setOutput( default_override=True, **render_data ):
    ''' Sets up basic parameters for rendering. Specifics are pulled from 'project' global 
    parameters module.'''
    if (default_override):
        render_data = database.getProduction('DEFAULT')
        render_data['output_path'] = ''
        render_data['multi_path'] = ''

    res    = (render_data['xres'], render_data['yres'])
    frate  = int(render_data['frate'])
    aspect = 1.7777

    doc    = core.doc()
    rd     = c4d.documents.RenderData()

    # GLOBAL SETTINGS
    doc.SetFps(frate)
    # Output paths
    rd[c4d.RDATA_PATH]            = str(render_data['output_path'])
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
    if not (render_data['output_path'] == ''):
        rd[c4d.RDATA_MULTIPASS_FILENAME] = str(render_data['multi_path'])
    # Format options
    rd[c4d.RDATA_MULTIPASS_SAVEFORMAT] = c4d.FILTER_PNG
    rd[c4d.RDATA_MULTIPASS_SAVEDEPTH]  = c4d.RDATA_FORMATDEPTH_16
    # Raytracing overrides
    rd[c4d.RDATA_RAYDEPTH]        = 5
    rd[c4d.RDATA_REFLECTIONDEPTH] = 2
    rd[c4d.RDATA_SHADOWDEPTH]     = 2
    # Miscellaneous
    rd[c4d.RDATA_TEXTUREERROR]    = True

    for mp in render_data['passes']:
        mp_obj = c4d.BaseList2D(c4d.Zmultipass)
        mp_obj.GetDataInstance()[c4d.MULTIPASSOBJECT_TYPE] = mp
        rd.InsertMultipass(mp_obj)

    core.createRenderData(rd, 'DEFAULT')
    return


# UI OBJECTS ######################################################################################
class ProjectInitWindow(gui.GeDialog):
    def __init__(self, populate=False):
        self.LBL_PROD_NAME    = 1000
        self.LBL_PROJECT_NAME = 1001
        self.LBL_SCENE_NAME   = 1002
        self.LBL_FRAMERATE    = 1003
        self.LBL_PREVIEW_DIR  = 1004
        self.LBL_PREVIEW_SCN  = 1005

        self.TXT_PROJECT_NAME = 2001
        self.TXT_SCENE_NAME   = 2002
        self.TXT_PREVIEW_DIR  = 2004
        self.TXT_PREVIEW_SCN  = 2005

        self.DRP_PROD_NAME    = 3000
        self.DRP_PROJ_NAME    = 3001
        self.CHK_EXISTING     = 3002

        self.RDO_FRAMERATE    = 3003
        self.RDO_FRAMERATE_T  = 3030
        self.RDO_FRAMERATE_S  = 3060
        self.BTN_EXECUTE      = 3009
        self.BTN_CANCEL       = 3010

        self.GROUP_MAIN       = 9000
        self.GROUP_BTNS       = 9001
        self.GROUP_PROJ       = 9002

        self.PRODUCTION_ID    = {}
        self.PRODUCTION_ITR   = 10000

        self.PROJECT_ID       = {}
        self.PROJECT_ITR      = 10001

        for proj in database.getAllProductions():
            self.PRODUCTION_ID[self.PRODUCTION_ITR] = proj
            self.PRODUCTION_ITR += 1


    def CreateLayout(self):
        # Headers
        self.SetTitle('Create New Project')        
        self.GroupBegin(self.GROUP_MAIN, c4d.BFH_LEFT, 2, 1)
        # Show selection dropdown
        self.AddStaticText(self.LBL_PROD_NAME, c4d.BFH_LEFT, name='Select Production:')
        self.AddComboBox(self.DRP_PROD_NAME, c4d.BFH_LEFT, 600)
        for proj in self.PRODUCTION_ID:
            self.AddChild(self.DRP_PROD_NAME, proj, self.PRODUCTION_ID[proj])
        # Project text field 
        self.AddStaticText(self.LBL_PROJECT_NAME, c4d.BFH_LEFT, name='Project Name:')
        self.GroupBegin(self.GROUP_PROJ, c4d.BFH_LEFT, 1, 3)
        self.AddCheckbox(self.CHK_EXISTING, c4d.BFH_LEFT, 600, 10, 'New Project')
        self.AddComboBox(self.DRP_PROJ_NAME, c4d.BFH_LEFT, 600)
        self.AddEditText(self.TXT_PROJECT_NAME, c4d.BFH_LEFT, 600)
        self.GroupEnd()
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

        # populate the fields if this is an exisitng project
        if (Scene.getSceneStatus()[2] == error.SCENE_OK):
            msg    = 'This will migrate your existing scene to a new project.  Use \'Scene Rename\' utility to simply make a new version of this project.'
            prompt = gui.MessageDialog(msg, c4d.GEMB_OKCANCEL)
            if (prompt == c4d.GEMB_R_OK):
                self.populate()
            elif (prompt == c4d.GEMB_R_CANCEL):
                self.Close()
                return False

        return True


    def Command(self, id, msg):
        if (id == self.BTN_EXECUTE):
            self.ok = True
            self.execute()
            self.Close()
        elif (id == self.BTN_CANCEL):
            self.Close()
        elif (id == self.TXT_PROJECT_NAME or
              id == self.TXT_SCENE_NAME):
            self.preview_fast()
        elif (id == self.DRP_PROJ_NAME or
              id == self.DRP_PROD_NAME or
              id == self.CHK_EXISTING):
            self.update_dropdown()
            self.preview_fast()
        return True


    def execute(self):
        show_name  = self.PRODUCTION_ID[self.GetInt32(self.DRP_PROD_NAME)]
        proj_name  = self.GetString(self.TXT_PROJECT_NAME)
        scene_name = self.GetString(self.TXT_SCENE_NAME)
        framerate  = self.GetInt32(self.RDO_FRAMERATE)-3000

        scene_ctrl, tag   = Scene.makeSceneCtrl()
        annotation        = "Production: {}\nProject: {}\nScene: {}\nFramerate: {}\nVersion: {}"
        annotation        = annotation.format(show_name, proj_name, scene_name, str(framerate), str(1))
        tag[c4d.ANNOTATIONTAG_TEXT] = annotation

        scn = Scene()
        scn.makeFolders()
        scn.setTakes()
        scn.setOutput()
        scn.saveWithBackup()

        return True


    def preview_fast(self):
        try:
            new_proj = self.GetBool(self.CHK_EXISTING)

            self.Enable(self.TXT_PROJECT_NAME, new_proj)
            self.Enable(self.DRP_PROJ_NAME, 1-new_proj)

            show_name  = self.PRODUCTION_ID[self.GetInt32(self.DRP_PROD_NAME)]
            if not (new_proj):
                proj_name = self.PROJECT_ID[self.GetInt32(self.DRP_PROJ_NAME)]
            else:
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
        except:
            pass
        return True


    def update_dropdown(self):
        try:
            if not self.GetBool(self.CHK_EXISTING):
                all_projects = database.getAllProjects(self.PRODUCTION_ID[self.GetInt32(self.DRP_PROD_NAME)])
                for proj in all_projects:
                    self.PROJECT_ID[self.PROJECT_ITR] = proj
                    self.PROJECT_ITR += 1
                for proj in self.PROJECT_ID: 
                    self.AddChild(self.DRP_PROJ_NAME, proj, self.PROJECT_ID[proj])
            else:
                self.FreeChildren(self.DRP_PROJ_NAME)
        except:
            pass


    def populate(self):
        scn = Scene()
        doc = core.doc()
        fps = doc.GetFps()

        for k,v in self.PRODUCTION_ID.iteritems():
            if (v == scn.production):
                prod_id = k
                break

        self.SetInt32(self.DRP_PROD_NAME, prod_id)
        self.SetString(self.TXT_PROJECT_NAME, '')
        self.SetString(self.TXT_SCENE_NAME, '')
        self.SetInt32(self.RDO_FRAMERATE, 3000+fps)
        self.SetBool(self.CHK_EXISTING, True)
        self.preview_fast()


class TeamColorWindow(gui.GeDialog):
    def __init__(self):
        self.LBL_HOME_TRICODE = 1000
        self.LBL_AWAY_TRICODE = 1001
        self.LBL_HOME_COLORF  = 2000
        self.LBL_AWAY_COLORF  = 2001

        self.TXT_HOME_TRICODE = 3000
        self.TXT_AWAY_TRICODE = 3001

        self.VEC_HOME_COLOR_P = 4000
        self.VEC_HOME_COLOR_S = 4001
        self.VEC_HOME_COLOR_T = 4002
        self.VEC_AWAY_COLOR_P = 4003
        self.VEC_AWAY_COLOR_S = 4004
        self.VEC_AWAY_COLOR_T = 4005


        self.BOOL_SWAP_PRISEC = 4050

        self.BTN_EXECUTE      = 5000
        self.BTN_CANCEL       = 5001

        self.GROUP_MAIN       = 9000
        self.GROUP_ROW1       = 9001
        self.GROUP_ROW2       = 9002
        self.GROUP_BTNS       = 9003

        self.left             = c4d.BFH_LEFT
        self.center           = c4d.BFH_CENTER
        self.right            = c4d.BFH_RIGHT

        self.prod = getSceneData()['Production']


    def CreateLayout(self):
        self.SetTitle('Team Color Picker')
        self.GroupBegin(self.GROUP_MAIN, self.left, 1, 2)

        self.GroupBegin(self.GROUP_ROW1, self.left, 5, 1)
        self.AddStaticText(self.LBL_HOME_TRICODE, self.left, initw=110, name='Home Team:')
        self.AddEditText(self.TXT_HOME_TRICODE, self.left, 100)
        self.AddColorField(self.VEC_HOME_COLOR_P, self.left)
        self.AddColorField(self.VEC_HOME_COLOR_S, self.left)
        self.AddColorField(self.VEC_HOME_COLOR_T, self.left)
        self.GroupEnd()

        self.GroupBegin(self.GROUP_ROW2, self.left, 5, 1)
        self.AddStaticText(self.LBL_AWAY_TRICODE, self.left, initw=110, name='Away Team:')
        self.AddEditText(self.TXT_AWAY_TRICODE, self.left, 100)
        self.AddColorField(self.VEC_AWAY_COLOR_P, self.left)
        self.AddColorField(self.VEC_AWAY_COLOR_S, self.left)
        self.AddColorField(self.VEC_AWAY_COLOR_T, self.left)
        self.GroupEnd()

        self.GroupBegin(self.GROUP_BTNS, self.right, 2, 1)
        self.AddButton(self.BTN_CANCEL, c4d.BFH_SCALE, name="Cancel")
        self.AddButton(self.BTN_EXECUTE, c4d.BFH_SCALE, name="Assign Colors")
        self.GroupEnd()

        self.GroupEnd()
        self.ok=False
        return True


    def Command(self, id, msg):
        if (id == self.TXT_HOME_TRICODE or id == self.TXT_AWAY_TRICODE):
            self.updateSwatches()
        elif (id == self.BTN_EXECUTE):
            self.updateMaterials()
            self.Close()
        elif (id == self.BTN_CANCEL):
            self.Close()
        return True


    def updateSwatches(self):
        home_tricode = self.GetString(self.TXT_HOME_TRICODE)
        away_tricode = self.GetString(self.TXT_AWAY_TRICODE)

        home_tricode

        try: 
            home_colors = database.getTeamColors(self.prod, home_tricode)
            home_team = True
        except: 
            home_team = None
        
        try: 
            away_colors = database.getTeamColors(self.prod, away_tricode)
            away_team = True
        except: 
            away_team = None

        if (home_team):
            self.SetColorField(self.VEC_HOME_COLOR_P, home_colors['primary'], 1.0, 1.0, c4d.DR_COLORFIELD_NO_BRIGHTNESS)
            self.SetColorField(self.VEC_HOME_COLOR_S, home_colors['secondary'], 1.0, 1.0, c4d.DR_COLORFIELD_NO_BRIGHTNESS)
            self.SetColorField(self.VEC_HOME_COLOR_T, home_colors['tertiary'], 1.0, 1.0, c4d.DR_COLORFIELD_NO_BRIGHTNESS)
        else:
            self.SetColorField(self.VEC_HOME_COLOR_P, c4d.Vector(0,0,0), 1.0, 1.0, c4d.DR_COLORFIELD_NO_BRIGHTNESS)
            self.SetColorField(self.VEC_HOME_COLOR_S, c4d.Vector(0,0,0), 1.0, 1.0, c4d.DR_COLORFIELD_NO_BRIGHTNESS)
            self.SetColorField(self.VEC_HOME_COLOR_T, c4d.Vector(0,0,0), 1.0, 1.0, c4d.DR_COLORFIELD_NO_BRIGHTNESS)

        if (away_team):
            self.SetColorField(self.VEC_AWAY_COLOR_P, away_colors['primary'], 1.0, 1.0, c4d.DR_COLORFIELD_NO_BRIGHTNESS)
            self.SetColorField(self.VEC_AWAY_COLOR_S, away_colors['secondary'], 1.0, 1.0, c4d.DR_COLORFIELD_NO_BRIGHTNESS)
            self.SetColorField(self.VEC_AWAY_COLOR_T, away_colors['tertiary'], 1.0, 1.0, c4d.DR_COLORFIELD_NO_BRIGHTNESS)
        else:
            self.SetColorField(self.VEC_AWAY_COLOR_P, c4d.Vector(0,0,0), 1.0, 1.0, c4d.DR_COLORFIELD_NO_BRIGHTNESS)
            self.SetColorField(self.VEC_AWAY_COLOR_S, c4d.Vector(0,0,0), 1.0, 1.0, c4d.DR_COLORFIELD_NO_BRIGHTNESS)
            self.SetColorField(self.VEC_AWAY_COLOR_T, c4d.Vector(0,0,0), 1.0, 1.0, c4d.DR_COLORFIELD_NO_BRIGHTNESS)
        return True


    def updateMaterials(self):
        home_pri = self.GetColorField(self.VEC_HOME_COLOR_P)['color']
        home_sec = self.GetColorField(self.VEC_HOME_COLOR_S)['color']
        home_tri = self.GetColorField(self.VEC_HOME_COLOR_T)['color']

        away_pri = self.GetColorField(self.VEC_AWAY_COLOR_P)['color']
        away_sec = self.GetColorField(self.VEC_AWAY_COLOR_S)['color']
        away_tri = self.GetColorField(self.VEC_AWAY_COLOR_T)['color']

        core.changeColor('HOME_PRIMARY', home_pri, exact=False)
        core.changeColor('HOME_SECONDARY', home_sec, exact=False)
        core.changeColor('HOME_TERTIARY', home_tri, exact=False)

        core.changeColor('AWAY_PRIMARY', away_pri, exact=False)
        core.changeColor('AWAY_SECONDARY', away_sec, exact=False)
        core.changeColor('AWAY_TERTIARY', away_tri, exact=False)
        return True


def test():
    t = ProjectInitWindow()
    t.Open(c4d.DLG_TYPE_MODAL, defaultw=300, defaulth=100)