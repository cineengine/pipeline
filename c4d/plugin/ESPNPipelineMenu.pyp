# coding: UTF-8

""" ESPNPipelineMenu.pyp: A Python plugin for Cinema 4D housing various pipeline utilities. """
__author__     = "Mark Rohrer"
__copyright__  = "Copyright 2017, ESPN Productions"
__credits__    = ["Mark Rohrer", "Martin Weber"]
__license__    = "Educational use only"
__version__    = "1.1-dev"
__maintainer__ = "Mark Rohrer"
__email__      = "mark.rohrer@espn.com"
__status__     = "Pre-deployment"

# internal libraries
import c4d
import os
from c4d import gui, bitmaps, plugins
# custom libraries
from pipeline.c4d import core 
from pipeline.c4d import scene
from pipeline.c4d import debug
from pipeline.c4d import database
from pipeline.c4d import submit
from pipeline.c4d import gvars
import pipeline.c4d.automation as auto
reload(core)
reload(scene)
reload(debug)
reload(database)
reload(submit)
reload(auto)

debug.info("Loaded ESPN Pipeline plug-in for C4D", __version__)

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
RDO_FRAMERATE_24     = 10024
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
BTN_PNG_OUTPUT       = 20002
BTN_EXR_OUTPUT       = 20003
BTN_NEWTAKE          = 20004
BTN_VERSIONUP        = 20005
BTN_SUBMIT           = 20006
LBL_OUTPUT_PATHS     = 20007
LBL_TAKE_UTILS       = 20008
BTN_CREATE_OBJBUFFERS= 20009
DRP_PRES_NAME        = 20010

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

DRP_PRES_NAME_START_ID=70000
DRP_PROJ_NAME_START_ID=80000
DRP_PROD_NAME_START_ID=90000

class ESPNMenu(gui.GeDialog):


    def __init__(self):
        self.this_scene = scene.MetaScene()
        self.this_doc   = c4d.documents.GetActiveDocument()

        self.prod_dict = {}
        self.prod_id   = DRP_PROD_NAME_START_ID
        self.prod_dict[self.prod_id] = ''
        self.reset_context_dropdowns()

        self.proj_use_existing= False
        self.prod_selected    = False
        self.matchup_selected = False

    def CreateLayout(self):
        self.LoadDialogResource(ESPNPipelineMenu)
        self.Enable(TXT_PREVIEW_PROJ, False)
        self.Enable(TXT_PREVIEW_FILE, False)

        self.retrieve_prod_list()
        self.populate()
        
        #self.refresh_preview_text()

        #self.toggle_matchup()

        #self.SetTimer(500)

        return True

    #def Timer(self, msg):
    #    if not (c4d.documents.GetActiveDocument() == self.this_doc):
    #        self.populate()
    #        self.this_doc = c4d.documents.GetActiveDocument()

    def Command(self, id, msg):
        # "Use existing project" checkbox
        if (id == CHK_EXISTING):
            self.toggle_use_existing_project()
        # "Production" dropdown
        elif (id == DRP_PROD_NAME):
            self.changed_production()
            #self.refresh_preview()
        # Text fields or "project" dropdown
        elif (id == TXT_PROJ_NAME or
              id == TXT_SCENE_NAME):
            self.refresh_preview_text()
        elif (id == DRP_PROJ_NAME):
            self.changed_project()
        # Render presets dropdown
        elif (id == DRP_PRES_NAME):
            self.push_render_preset()
        # "Create new" button
        elif (id == BTN_NEWPROJ_EXEC):
            self.create_new_scene()
        elif (id == BTN_HELP_EXEC):
            self.help('tab1')
        # tab 2 buttons
        elif (id == BTN_SETOUTPUT):
            self.push_output_paths()
        elif (id == BTN_SUBMIT):
            self.submit_to_farm()
        elif (id == BTN_NEWTAKE):
            self.create_take()
        elif (id == BTN_PNG_OUTPUT):
            self.push_png_output()
        elif (id == BTN_EXR_OUTPUT):
            self.push_exr_output()
        # tab 3
        elif (id == IS_MATCHUP):
            self.toggle_matchup()
        elif (id == TXT_HOME_TRICODE or
              id == TXT_AWAY_TRICODE):
            self.retrieve_swatches()
        elif (id == HOME_PRIMARY_EXEC):
            self.create_team_color_material('home', 'primary')
        elif (id == HOME_SECONDARY_EXEC):
            self.create_team_color_material('home', 'secondary')
        elif (id == HOME_TERTIARY_EXEC):
            self.create_team_color_material('home', 'tertiary')
        elif (id == AWAY_PRIMARY_EXEC):
            self.create_team_color_material('away', 'primary')
        elif (id == AWAY_SECONDARY_EXEC):
            self.create_team_color_material('away', 'secondary')
        elif (id == AWAY_TERTIARY_EXEC):
            self.create_team_color_material('away', 'tertiary')
        elif (id == TEAM_SWITCH_EXEC):
            self.push_team_colors()
        elif (id == AUTOMATION_HELP_EXEC):
            self.help('tab3')
        elif (id == SAVE_BACKUP_EXEC):
            self.save()
        elif (id == RENAME_EXEC):
            self.rename()
        elif (id == BTN_VERSIONUP):
            self.version_up()
        elif (id == SAVE_RENAME_HELP_EXEC):
            self.help('save_rename')
        elif (id == RELINK_TEXTURES_EXEC):
            auto.relinkTextures(migrate=True)
        elif (id == BTN_CREATE_OBJBUFFERS):
            self.createObjectBuffers()
        return True

    ### TAB 01 FUNCTIONS #####################################################
    def populate(self):
        ''' Populates the UI with initial values. Pulls in data from a 
        pipelined scene (if applicable).'''
        # set default values
        self.toggle_prod_selected(False)
        self.SetBool(CHK_EXISTING, False)
        self.SetInt32(RDO_FRAMERATE, RDO_FRAMERATE_30)

        if (self.this_scene.is_tagged()):
            fps = c4d.documents.GetActiveDocument().GetFps()
            # get id of current production from the dict value
            for k,v in self.prod_dict.iteritems():
                if (v == self.this_scene.production):
                    self.prod_id = k

            # set the production dropdown and get the project dropdown ready
            self.SetInt32(DRP_PROD_NAME, self.prod_id)
            self.SetBool(CHK_EXISTING, True)
            self.retrieve_projects()
            # get id of current project from the dict value
            self.proj_id = DRP_PROJ_NAME_START_ID
            for k,v in self.proj_dict.iteritems():
                if (v == self.this_scene.project_name):
                    self.proj_id = k

            # set the project dropdown
            self.SetInt32(DRP_PROJ_NAME, self.proj_id)
            self.Enable(TXT_PROJ_NAME, False)
            # set the scene name and framerate
            self.SetString(TXT_SCENE_NAME, self.this_scene.scene_name)
            self.SetInt32(RDO_FRAMERATE, 10000+fps)
            self.toggle_prod_selected(True)

    def validate_fields(self):
        pass

    def toggle_use_existing_project(self):
        # Query checkbox
        chk = self.GetBool(CHK_EXISTING)
        self.use_existing = chk
        # Activate / deactivate relevant fields
        self.Enable(DRP_PROJ_NAME, chk)
        self.Enable(TXT_PROJ_NAME, 1-chk)
        # Set the project id internally
        if (chk): self.proj_id = self.GetInt32(DRP_PROJ_NAME)
        else:     self.proj_id = DRP_PROJ_NAME_START_ID
        # Update the text preview
        self.refresh_preview_text()

    def changed_production(self):
        # Update UI variables with new selection
        self.prod_id = self.GetInt32(DRP_PROD_NAME)
        # Reset production-depdendent context dropdowns
        self.reset_context_dropdowns()
        # Refresh the UI with new values
        if not (self.GetInt32(DRP_PROD_NAME) == 0):
            self.toggle_prod_selected(True)
            # update the project list
            self.retrieve_projects()
            # update the preset list
            self.retrieve_presets()
            # .. & refresh previews
            self.SetInt32(DRP_PROJ_NAME, DRP_PROJ_NAME_START_ID)
            self.SetInt32(DRP_PRES_NAME, DRP_PRES_NAME_START_ID)
            #self.populate()
        else:
            self.toggle_prod_selected(False)
        self.refresh_preview_text()

    def changed_project(self):
        self.proj_id = self.GetInt32(DRP_PROJ_NAME)
        self.refresh_preview_text()

    def changed_preset(self):
        self.pres_id = self.GetInt32(DRP_PRES_NAME)

    def reset_context_dropdowns(self):
        self.proj_dict = {}
        self.pres_dict = {}
        self.proj_id   = DRP_PROJ_NAME_START_ID
        self.pres_id   = DRP_PRES_NAME_START_ID
        self.proj_dict[self.proj_id] = ''
        self.pres_dict[self.pres_id] = ''
        try:
            self.FreeChildren(DRP_PROJ_NAME)
            self.FreeChildren(DRP_PRES_NAME)
            self.SetInt32(DRP_PROJ_NAME, self.proj_id)
            self.SetInt32(DRP_PRES_NAME, self.pres_id)
        except: pass

    def refresh_preview_text(self):
        ''' Updates preview text fields (when typing or changing dropdowns)'''
        # parse ui fields into string values
        prod_name = self.prod_dict[self.prod_id]
        if self.GetBool(CHK_EXISTING):
            proj_name = self.proj_dict[self.proj_id]
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

    def retrieve_prod_list(self):
        # generate a dictionary with gui ID as key and name as value
        id_ = DRP_PROD_NAME_START_ID
        for prod in database.getAllProductions():
            id_ += 1
            self.prod_dict[id_] = prod
        # tab1_populate production list
        for id_ in self.prod_dict:
            self.AddChild(DRP_PROD_NAME, id_, self.prod_dict[id_])

    def retrieve_projects(self):
        # generate a dictionary with gui ID as key and name as value
        id_ = DRP_PROJ_NAME_START_ID
        for proj in database.getAllProjects(self.prod_dict[self.prod_id]):
            id_ += 1
            self.proj_dict[id_] = proj
            #print "retrieve_projects(): {}".format(id_)
        # tab1_populate project list
        for id_ in self.proj_dict:
            self.AddChild(DRP_PROJ_NAME, id_, self.proj_dict[id_])

    def retrieve_presets(self):
        id_ = DRP_PRES_NAME_START_ID
        for pres in database.getAllPresets(self.prod_dict[self.prod_id]):
            id_ += 1
            self.pres_dict[id_] = pres
            #print "retrieve_presets(): {}".format(id_)
        for id_ in self.pres_dict:
            self.AddChild(DRP_PRES_NAME, id_, self.pres_dict[id_])

    def toggle_prod_selected(self, bool_):
        ''' Since the UI defaults to not having a production selected, most
        fields are disabled. When a production *is* selected, this method
        enables the dependent fields.'''
        self.prod_selected = bool_
        self.Enable(CHK_EXISTING, bool_)
        self.Enable(DRP_PROJ_NAME, bool_)
        self.Enable(TXT_PROJ_NAME, bool_)
        self.Enable(TXT_SCENE_NAME, bool_)
        self.Enable(RDO_FRAMERATE, bool_)
        if (bool_ == True):
            chk = self.GetBool(CHK_EXISTING)
            self.Enable(DRP_PROJ_NAME, chk)
            self.Enable(TXT_PROJ_NAME, 1-chk) 

    def toggle_matchup(self):
        chk = self.GetBool(IS_MATCHUP)
        self.matchup_selected = chk
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
    """
    def create_new_scene(self):
        # populate strings from text fields
        prod_name = self.production_enum[self.GetInt32(DRP_PROD_NAME)]
        if (self.GetBool(CHK_EXISTING) == True):
            proj_name = self.project_enum[self.GetInt32(DRP_PROJ_NAME)]
        else:
            proj_name = self.GetString(TXT_PROJ_NAME)
        scene_name = self.GetString(TXT_SCENE_NAME)
        framerate  = self.GetInt32(RDO_FRAMERATE)-10000
        # cancel if any required fields are empty
        self.this_scene = scene.MetaScene.from_data
        (
            {
            'production'  : prod_name,
            'project_name': proj_name,
            'scene_name'  : scene_name,
            'framerate'   : framerate,
            'version'     : 1
            }
        )
        return True"""

    def help(self, tab):
        help_diag = ESPNHelp(panel=tab)
        help_diag.Open(dlgtype=c4d.DLG_TYPE_MODAL, xpos=-1, ypos=-1)
        return True

    ### TAB 02 FUNCTIONS #########################################################################
    def push_output_paths(self):
        self.this_scene._set_rscene_output_paths()

    def submit_to_farm(self):
        dlg = submit.SubmissionDialog()
        dlg.Open(c4d.DLG_TYPE_MODAL, defaultw=300, defaulth=50)

    def create_take(self):
        name = gui.RenameDialog('')
        if not (name == ''):
            core.take(name, set_active=False)
        else: pass
        return True

    def push_png_output(self):
        core.setOutputFiletype('png', 16)

    def push_exr_output(self):
        core.setOutputFiletype('exr')

    ### TAB 03 FUNCTIONS #########################################################################
    def push_team_colors(self):
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

    def retrieve_swatches(self):
        home_tricode = self.GetString(TXT_HOME_TRICODE)
        away_tricode = self.GetString(TXT_AWAY_TRICODE)

        try:
            home_colors = database.getTeamColors(self.this_scene.production, home_tricode, squelch=True)
            home_team = True
        except:
            home_team = None
        try:
            away_colors = database.getTeamColors(self.this_scene.production, away_tricode, squelch=True)
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

    def create_team_color_material(self, location, swatch):
        location = location.upper()
        swatch   = swatch.upper()
        name     = '{0}_{1}'.format(location, swatch)

        core.createMaterial(name)

    ### SAVE / RENAME SCENE TAB ##################################################################
    def save(self):
        self.this_scene.save()
        return True

    def rename(self):
        self.this_scene.rename()
        return True

    def version_up(self):
        self.this_scene.version_up()
        return True

    def createObjectBuffers(self):
        if len(core.getCheckedTakes()):
            scene.createObjectBuffers(consider_takes=True)
        else:
            scene.createObjectBuffers(consider_takes=False)

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