# !/usr/bin/env python
# coding: UTF-8

""" ESPNPipelineMenu.pyp: A Python plugin for Cinema 4D housing various pipeline utilities. """

__author__     = "Mark Rohrer"
__copyright__  = "Copyright 2016, ESPN Productions"
__credits__    = ["Mark Rohrer", "Martin Weber"]
__license__    = "GPL"
__version__    = "0.85"
__maintainer__ = "Mark Rohrer"
__email__      = "mark.rohrer@espn.com"
__status__     = "Beta testing"

# internal libraries
import c4d
import os
from c4d import gui, bitmaps, plugins
# custom libraries
from pipeline.c4d import core
from pipeline.c4d import scene
from pipeline.c4d import error
from pipeline.c4d import database
from pipeline.c4d import submit
import pipeline.c4d.automation as auto
reload(core)
reload(scene)
reload(error)
reload(database)
reload(submit)
reload(auto)

PLUGIN_ID = 1037160
BUTTON_ID = 1037183

ID_STATIC            = 99999
ESPNPipelineMenu     = 10000
ESPNHelpMenu         = 99998
CLOSE                = 99997
MAIN_DIALOG          = 10001

FIRST_TAB            = 10002
LBL_PROD_NAME        = 10004
DRP_PROD_NAME        = 10005
LBL_PROJ_NAME        = 10006
CHK_EXISTING         = 10007
DRP_PROJ_NAME        = 10008
TXT_PROJ_NAME        = 10009
LBL_SCENE_NAME       = 10010
TXT_SCENE_NAME       = 10011
LBL_FRAMERATE        = 10012
RDO_FRAMERATE        = 10013
RDO_FRAMERATE_30     = 10030
RDO_FRAMERATE_60     = 10060
FIRST_TAB_SEP_01     = 10017
LBL_PREVIEW          = 10018
LBL_PREVIEW_NULL     = 10118
LBL_PREVIEW_PROJ     = 10019
TXT_PREVIEW_PROJ     = 10020
LBL_PREVIEW_FILE     = 10021
TXT_PREVIEW_FILE     = 10022
BTN_NEWPROJ_EXEC     = 10023
BTN_HELP_EXEC        = 10024
HELP_IMAGE           = 10029

SECOND_TAB           = 20000
BTN_SETOUTPUT        = 20001
BTN_MAKETAG          = 20002
BTN_SORT             = 20003
BTN_NEWTAKE          = 20004
BTN_VERSIONUP        = 20005
BTN_SUBMIT           = 20006
LBL_OUTPUT_PATHS     = 20007
LBL_TAKE_UTILS       = 20008
BTN_CREATE_OBJBUFFERS= 20009

THIRD_TAB            = 30000
LBL_HOME_TRICODE     = 30001
TXT_HOME_TRICODE     = 30002
VEC_HOME_COLOR_P     = 30003
VEC_HOME_COLOR_S     = 30004
VEC_HOME_COLOR_T     = 30005
LBL_AWAY_TRICODE     = 30006
TXT_AWAY_TRICODE     = 30007
VEC_AWAY_COLOR_P     = 30008
VEC_AWAY_COLOR_S     = 30009
VEC_AWAY_COLOR_T     = 30010
THIRD_TAB_INSTRUCTION= 30011
IS_MATCHUP           = 30012
TEAM_SWITCH_EXEC     = 30013
HOME_PRIMARY_EXEC    = 30014
HOME_SECONDARY_EXEC  = 30015
HOME_TERTIARY_EXEC   = 30016
AWAY_PRIMARY_EXEC    = 30017
AWAY_SECONDARY_EXEC  = 30018
AWAY_TERTIARY_EXEC   = 30019
AUTOMATION_HELP_EXEC = 30020

SAVE_RENAME_TAB      = 40000
SAVE_BACKUP_EXEC     = 40001
RENAME_EXEC          = 40002
SAVE_RENAME_HELP_EXEC= 40003
RELINK_TEXTURES_EXEC = 40004

DRP_PROJ_NAME_START_ID=80000
DRP_PROD_NAME_START_ID=90000

class ESPNMenu(gui.GeDialog):
    def __init__(self):
        self.production_enum    = {}
        self.production_ids     = []
        self.production_enum[0] = ''

        self.project_enum    = {}
        self.project_ids     = []
        self.project_enum[0] = ''

    def CreateLayout(self):
        self.LoadDialogResource(ESPNPipelineMenu)
        sc, st, status = scene.Scene.getSceneStatus()
        self.tab1_pullProductionList()

        if (status == error.SCENE_OK):
            self.this_scene = scene.Scene()
            self.tab1_populate(existing=True)
        else: 
            self.tab1_populate(existing=False)

        self.SetInt32(RDO_FRAMERATE, RDO_FRAMERATE_30)
        self.tab3_matchupEnabled()

        return True

    def Command(self, id, msg):
        # "Use existing project" checkbox
        if (id == CHK_EXISTING):
            chk = self.GetBool(CHK_EXISTING)
            self.Enable(DRP_PROJ_NAME, chk)
            self.Enable(TXT_PROJ_NAME, 1-chk)
            self.tab1_refresh()
        # "Production" dropdown
        elif (id == DRP_PROD_NAME):
             self.tab1_refresh(projects=True)
        # Text fields or "project" dropdown
        elif (id == TXT_PROJ_NAME or
              id == TXT_SCENE_NAME or
              id == DRP_PROJ_NAME):
            self.tab1_refresh()
        # "Create new" button
        elif (id == BTN_NEWPROJ_EXEC):
            self.tab1_create()
        elif (id == BTN_HELP_EXEC):
            self.help('tab1')
        # tab 2 buttons
        elif (id == BTN_SETOUTPUT):
            self.tab2_setOutput()
        elif (id == BTN_SUBMIT):
            self.tab2_submit()
        elif (id == BTN_NEWTAKE):
            self.tab2_newTake()
        elif (id == BTN_MAKETAG):
            self.tab2_addTag()
        elif (id == BTN_SORT):
            self.tab2_sortScene()
        # tab 3
        elif (id == IS_MATCHUP):
            self.tab3_matchupEnabled()
        elif (id == TXT_HOME_TRICODE or
              id == TXT_AWAY_TRICODE):
            self.tab3_updateSwatches()
        elif (id == HOME_PRIMARY_EXEC):
            self.tab3_createTeamColorMat('home', 'primary')
        elif (id == HOME_SECONDARY_EXEC):
            self.tab3_createTeamColorMat('home', 'secondary')
        elif (id == HOME_TERTIARY_EXEC):
            self.tab3_createTeamColorMat('home', 'tertiary')
        elif (id == AWAY_PRIMARY_EXEC):
            self.tab3_createTeamColorMat('away', 'primary')
        elif (id == AWAY_SECONDARY_EXEC):
            self.tab3_createTeamColorMat('away', 'secondary')
        elif (id == AWAY_TERTIARY_EXEC):
            self.tab3_createTeamColorMat('away', 'tertiary')
        elif (id == TEAM_SWITCH_EXEC):
            self.tab3_switchTeam()
        elif (id == AUTOMATION_HELP_EXEC):
            self.help('tab3')
        elif (id == SAVE_BACKUP_EXEC):
            self.tab4_saveWithBackup()
        elif (id == RENAME_EXEC):
            self.tab4_rename()
        elif (id == BTN_VERSIONUP):
            self.tab4_versionUp()
        elif (id == SAVE_RENAME_HELP_EXEC):
            self.help('save_rename')
        elif (id == RELINK_TEXTURES_EXEC):
            auto.relinkTextures(migrate=True)
        elif (id == BTN_CREATE_OBJBUFFERS):
            self.createObjectBuffers()
        return True

    ### TAB 01 FUNCTIONS #########################################################################
    def tab1_populate(self, existing=False):
        ''' Populates the UI with initial values.
            existing: Pulls in data from a pipelined scene (if applicable).'''
        # set default values
        self.tab1_prodSelected(False)
        self.SetBool(CHK_EXISTING, False)
        self.Enable(TXT_PREVIEW_PROJ, False)
        self.Enable(TXT_PREVIEW_FILE, False)

        if (existing):
            doc = c4d.documents.GetActiveDocument()
            fps = doc.GetFps()
            # get id of current production from the dict value
            for k,v in self.production_enum.iteritems():
                if (v == self.this_scene.production):
                    prod_id = k
            # set the production dropdown and get the project dropdown ready
            self.SetInt32(DRP_PROD_NAME, prod_id)
            self.tab1_refresh(preview=False, projects=True)
            self.SetBool(CHK_EXISTING, True)
            # get id of current project from the dict value
            proj_id = DRP_PROJ_NAME_START_ID
            for k,v in self.project_enum.iteritems():
                if (v == self.this_scene.project_name):
                    proj_id = k
            # set the project dropdown
            self.SetInt32(DRP_PROJ_NAME, proj_id)
            self.Enable(TXT_PROJ_NAME, False)
            # set the scene name and framerate
            self.SetString(TXT_SCENE_NAME, self.this_scene.scene_name)
            self.SetInt32(RDO_FRAMERATE, 10000+fps)
            # refresh to update preview values
            self.tab1_refresh()

    def tab1_refresh(self, preview=True, projects=False):
        ''' Updates the UI with selection or input changes.
            preview:  Updates preview text fields (when typing or changing dropdowns)
            projects:  Updates the project dropdown (when production selection changes)'''
        if (preview):
            # parse ui fields into string values
            prod_name = self.production_enum[self.GetInt32(DRP_PROD_NAME)]
            if self.GetBool(CHK_EXISTING):
                proj_name = self.project_enum[self.GetInt32(DRP_PROJ_NAME)]
                self.Enable(DRP_PROJ_NAME, True)
                self.Enable(TXT_PROJ_NAME, False)
            else:
                proj_name = self.GetString(TXT_PROJ_NAME)
                self.Enable(DRP_PROJ_NAME, False)
                self.Enable(TXT_PROJ_NAME, True)
            scene_name = self.GetString(TXT_SCENE_NAME)
            prod_folder = database.getProduction(prod_name)['project']
            # Don't allow spaces as the user types
            proj_name = proj_name.replace(' ', '_') 
            scene_name = scene_name.replace(' ', '_')
            self.SetString(TXT_PROJ_NAME, proj_name)
            self.SetString(TXT_SCENE_NAME, scene_name)
            # Generate preview paths
            scene_prev = '{0}_{1}.c4d'.format(proj_name, scene_name)
            proj_prev  = os.path.relpath(
                "{0}\\{1}\\c4d\\".format(prod_folder, proj_name),
                "Y:\\Workspace\\MASTER_PROJECTS\\"
                )
            self.SetString(TXT_PREVIEW_PROJ, proj_prev)
            self.SetString(TXT_PREVIEW_FILE, scene_prev)

        if (projects):
            if not (self.GetInt32(DRP_PROD_NAME) == 0):
                # flag it as such
                self.tab1_prodSelected(True)
                # update the project list
                self.tab1_pullProjectList()
                # .. & refresh previews
                self.tab1_refresh(preview=True, projects=False)

    def tab1_prodSelected(self, bool_):
        ''' Since the UI defaults to not having a production selected, most fields are disabled.
            When a production *is* selected, this method enables the dependent fields.'''
        self.Enable(CHK_EXISTING, bool_)
        self.Enable(DRP_PROJ_NAME, bool_)
        self.Enable(TXT_PROJ_NAME, bool_)
        self.Enable(TXT_SCENE_NAME, bool_)
        self.Enable(RDO_FRAMERATE, bool_)
        if (bool_ == True):
            chk = self.GetBool(CHK_EXISTING)
            self.Enable(DRP_PROJ_NAME, chk)
            self.Enable(TXT_PROJ_NAME, 1-chk) 

    def tab1_pullProductionList(self):
        # generate a dictionary with gui ID as key and name as value
        id_ = DRP_PROD_NAME_START_ID
        for prod in database.getAllProductions():
            self.production_enum[id_] = prod
            self.production_ids.append(id_)
            id_ += 1
        # tab1_populate production list
        for prod in self.production_enum:
            self.AddChild(DRP_PROD_NAME, prod, self.production_enum[prod])

    def tab1_pullProjectList(self):
        # generate a dictionary with gui ID as key and name as value
        id_ = DRP_PROJ_NAME_START_ID
        for proj in database.getAllProjects(self.production_enum[self.GetInt32(DRP_PROD_NAME)]):
            self.project_enum[id_] = proj
            self.project_ids.append(id_)
            id_ += 1
        # tab1_populate project list
        for proj in self.project_enum:
            self.AddChild(DRP_PROJ_NAME, proj, self.project_enum[proj])

    def tab1_create(self):
        # populate strings from text fields
        prod_name = self.production_enum[self.GetInt32(DRP_PROD_NAME)]
        if (self.GetBool(CHK_EXISTING) == True):
            proj_name = self.project_enum[self.GetInt32(DRP_PROJ_NAME)]
        else:
            proj_name = self.GetString(TXT_PROJ_NAME)
        scene_name = self.GetString(TXT_SCENE_NAME)
        framerate  = self.GetInt32(RDO_FRAMERATE)-10000
        # cancel if any required fields are empty
        if (scene_name == '' or
            proj_name  == ''):
            msg = 'Project or Scene name has not been set. Both are required to proceed.'
            gui.MessageDialog(msg, c4d.GEMB_OK)
            return False
        # check for existing scene controller
        scene_ctrl, scene_tag, status = scene.Scene.getSceneStatus()
        if (status == error.SCENE_OK):
            scene_ctrl.Remove()
        # create new scene controller
        scene_ctrl, scene_tag = scene.Scene.makeSceneCtrl()
        annotation = "Production: {0}\nProject: {1}\nScene: {2}\nFramerate: {3}\nVersion: {4}"
        annotation = annotation.format(prod_name, proj_name, scene_name, str(framerate), str(1))
        scene_tag[c4d.ANNOTATIONTAG_TEXT] = annotation
        # setup project and save
        scn = scene.Scene()
        scn.makeFolders()
        #scn.setTakes()
        scn.setOutput()
        auto.relinkTextures(migrate=True)
        scn.saveWithBackup()
        return True

    def help(self, tab):
        help_diag = ESPNHelp(panel=tab)
        help_diag.Open(dlgtype=c4d.DLG_TYPE_MODAL, xpos=-1, ypos=-1)
        return True


    ### TAB 02 FUNCTIONS #########################################################################
    def tab2_setOutput(self):
        chk = scene.Scene.isPipelined()
        if (chk):
            scn = scene.Scene()
            scn.setOutput()
        else:
            scene.Scene.setOutput()
        return True

    def tab2_submit(self):
        dlg = submit.SubmissionDialog()
        dlg.Open(c4d.DLG_TYPE_MODAL, defaultw=300, defaulth=50)

    def tab2_newTake(self):
        name = gui.RenameDialog('')
        if not (name == ''):
            core.take(name, set_active=False)
        else: pass
        return True

    def tab2_addTag(self):
        pass

    def tab2_sortScene(self):
        pass

    ### TAB 03 FUNCTIONS #########################################################################
    def tab3_switchTeam(self):
        chk = self.GetBool(IS_MATCHUP)
        values = {}

        values['home_primary'] = self.GetColorField(VEC_HOME_COLOR_P)
        values['home_secondary'] = self.GetColorField(VEC_HOME_COLOR_S)
        values['home_tertiary'] = self.GetColorField(VEC_HOME_COLOR_T)

        if (chk):
            values['away_primary'] = self.GetColorField(VEC_AWAY_COLOR_P)
            values['away_secondary'] = self.GetColorField(VEC_AWAY_COLOR_S)
            values['away_tertiary'] = self.GetColorField(VEC_AWAY_COLOR_T)

        for k,v in values.iteritems():
            core.changeColor(k.upper(), v['color'], exact=False)

    def tab3_updateSwatches(self):
        chk = scene.Scene.isPipelined()
        if (chk):
            self.this_scene = scene.Scene()
        else: return
        home_tricode = self.GetString(TXT_HOME_TRICODE)
        away_tricode = self.GetString(TXT_AWAY_TRICODE)

        try:
            home_colors = database.getTeamColors(self.this_scene.production, home_tricode)
            home_team = True
        except:
            home_team = None
        try:
            away_colors = database.getTeamColors(self.this_scene.production, away_tricode)
            away_team = True
        except:
            away_team = None

        if (home_team):
            self.SetColorField(VEC_HOME_COLOR_P, home_colors['primary'], 1.0, 1.0, c4d.DR_COLORFIELD_NO_BRIGHTNESS)
            self.SetColorField(VEC_HOME_COLOR_S, home_colors['secondary'], 1.0, 1.0, c4d.DR_COLORFIELD_NO_BRIGHTNESS)
            self.SetColorField(VEC_HOME_COLOR_T, home_colors['tertiary'], 1.0, 1.0, c4d.DR_COLORFIELD_NO_BRIGHTNESS)
        else:
            self.SetColorField(VEC_HOME_COLOR_P, c4d.Vector(0,0,0), 1.0, 1.0, c4d.DR_COLORFIELD_NO_BRIGHTNESS)
            self.SetColorField(VEC_HOME_COLOR_S, c4d.Vector(0,0,0), 1.0, 1.0, c4d.DR_COLORFIELD_NO_BRIGHTNESS)
            self.SetColorField(VEC_HOME_COLOR_T, c4d.Vector(0,0,0), 1.0, 1.0, c4d.DR_COLORFIELD_NO_BRIGHTNESS)

        if (away_team):
            self.SetColorField(VEC_AWAY_COLOR_P, away_colors['primary'], 1.0, 1.0, c4d.DR_COLORFIELD_NO_BRIGHTNESS)
            self.SetColorField(VEC_AWAY_COLOR_S, away_colors['secondary'], 1.0, 1.0, c4d.DR_COLORFIELD_NO_BRIGHTNESS)
            self.SetColorField(VEC_AWAY_COLOR_T, away_colors['tertiary'], 1.0, 1.0, c4d.DR_COLORFIELD_NO_BRIGHTNESS)
        else:
            self.SetColorField(VEC_AWAY_COLOR_P, c4d.Vector(0,0,0), 1.0, 1.0, c4d.DR_COLORFIELD_NO_BRIGHTNESS)
            self.SetColorField(VEC_AWAY_COLOR_S, c4d.Vector(0,0,0), 1.0, 1.0, c4d.DR_COLORFIELD_NO_BRIGHTNESS)
            self.SetColorField(VEC_AWAY_COLOR_T, c4d.Vector(0,0,0), 1.0, 1.0, c4d.DR_COLORFIELD_NO_BRIGHTNESS)
        return True

    def tab3_matchupEnabled(self):
        chk = self.GetBool(IS_MATCHUP)
        if (chk):
            self.Enable(TXT_AWAY_TRICODE, True)
            self.Enable(VEC_AWAY_COLOR_P, True)
            self.Enable(VEC_AWAY_COLOR_S, True)
            self.Enable(VEC_AWAY_COLOR_T, True)
        else:
            self.Enable(TXT_AWAY_TRICODE, False)
            self.Enable(VEC_AWAY_COLOR_P, False)
            self.Enable(VEC_AWAY_COLOR_S, False)
            self.Enable(VEC_AWAY_COLOR_T, False)

    def tab3_createTeamColorMat(self, location, swatch):
        location = location.upper()
        swatch   = swatch.upper()
        name     = '{0}_{1}'.format(location, swatch)

        core.createMaterial(name)

    ### SAVE / RENAME SCENE TAB ##################################################################
    def tab4_saveWithBackup(self):
        chk = scene.Scene.isPipelined()
        if (chk):
            self.this_scene = scene.Scene()
            self.this_scene.saveWithBackup()
        else: raise error.PipelineError(0)

    def tab4_rename(self):
        chk = scene.Scene.isPipelined()
        if (chk):
            self.this_scene = scene.Scene()
            self.this_scene.rename()
        else: raise error.PipelineError(0)

    def createObjectBuffers(self):
        if len(core.getCheckedTakes()):
            scene.Scene.createObjectBuffers(consider_takes=True)
        else:
            scene.Scene.createObjectBUffers(consider_takes=False)

    def tab4_versionUp(self):
        chk = scene.Scene.isPipelined()
        if (chk):
            scn = scene.Scene()
            scn.versionUp()
        else: raise error.PipelineError(0)
        return True

class ESPNHelp(gui.GeDialog):
    def __init__(self, panel):
        self.panel = panel

    def CreateLayout(self):
        self.LoadDialogResource(ESPNHelpMenu)
        try: 
            gui.GetIcon(BUTTON_ID)["bmp"].FlushAll()
            gui.UnregisterIcon(BUTTON_ID)
        except: pass
        dir, file = os.path.split(__file__)
        if (self.panel=='tab1'):
            fn = os.path.join(dir, "res", "icons", "tab1_help.tif")
        elif (self.panel=='tab3'):
            fn = os.path.join(dir, "res", "icons", "tab3_help.tif")
        elif (self.panel=='save_rename'):
            fn = os.path.join(dir, "res", "icons", "save_rename_help.tif")
        bmp = bitmaps.BaseBitmap()
        bmp.InitWith(fn)
        gui.RegisterIcon(BUTTON_ID, bmp)
        return True

class ESPNPipelinePlugin(plugins.CommandData):
    dialog = None

    def Execute(self, doc):
        if self.dialog is None:
            self.dialog = ESPNMenu()

        return self.dialog.Open(dlgtype=c4d.DLG_TYPE_ASYNC, pluginid=PLUGIN_ID, defaultw=300, defaulth=50)

    def RestoreLayout(self, sec_ref):
        if self.dialog is None:
            self.dialog = ESPNMenu()

        return self.dialog.Restore(pluginid=PLUGIN_ID, secret=sec_ref)

if __name__ == "__main__":
    bmp = bitmaps.BaseBitmap()

    dir, file = os.path.split(__file__)
    fn = os.path.join(dir, "res", "icons", "icon.png")
    bmp.InitWith(fn)

    #desc = plugins.GeLoadString(ESPNPipelineMenu)

    plugins.RegisterCommandPlugin(id=PLUGIN_ID,
                                  str="ESPN Pipeline",
                                  info=0,
                                  help="Main menu for ESPN pipeline operations",
                                  dat=ESPNPipelinePlugin(),
                                  icon=bmp)