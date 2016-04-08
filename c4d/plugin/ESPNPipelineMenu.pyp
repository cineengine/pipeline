# !/usr/bin/python
# coding: UTF-8

# internal libraries
import c4d
import os
from c4d import gui, bitmaps, plugins
# custom libraries
#from pipeline.c4d import scene
from pipeline.c4d import scene
from pipeline.c4d import error
from pipeline.c4d import database
reload(scene)
reload(error)
reload(database)

PLUGIN_ID = 1037160

ID_STATIC            = 99999
ESPNPipelineMenu     = 10000
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
BTN_MIGPROJ_EXEC     = 10024
BTN_RENAME_EXEC      = 10025
LBL_NEWPROJ_EXEC     = 10026
LBL_MIGPROJ_EXEC     = 10027
LBL_RENAME_EXEC      = 10028

SECOND_TAB           = 20000
SECOND_TAB_TEXT      = 20001
SECOND_TAB_TEXTBOX   = 20002

THIRD_TAB            = 30000
THIRD_TAB_TEXT       = 30001
THIRD_TAB_TEXTBOX    = 30002

FOURTH_TAB           = 40000
FOURTH_TAB_TEXT      = 40001
FOURTH_TAB_TEXTBOX   = 40002

DRP_PROJ_NAME_START_ID = 80000
DRP_PROD_NAME_START_ID = 90000

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
        self.pullProductionList()
        self.populate()

        if (status == error.SCENE_OK):
            self.this_scene = scene.Scene()
            self.populateExistingScene()
        return True

    def Command(self, id, msg):
        if (id == CHK_EXISTING):
            chk = self.GetBool(CHK_EXISTING)
            self.Enable(DRP_PROJ_NAME, chk)
            self.Enable(TXT_PROJ_NAME, 1-chk)
            self.refresh()
        elif (id == DRP_PROD_NAME):
             self.refreshProductionChange()
        elif (id == TXT_PROJ_NAME or
              id == TXT_SCENE_NAME or
              id == DRP_PROJ_NAME):
            self.refresh()
        return True

    def populate(self):
        # set default values
        self.productionSelected(False)
        self.SetBool(CHK_EXISTING, False)
        self.Enable(TXT_PREVIEW_PROJ, False)
        self.Enable(TXT_PREVIEW_FILE, False)

    def refresh(self):
        # parse ui fields
        prod_name = self.production_enum[self.GetInt32(DRP_PROD_NAME)]
        if self.GetBool(CHK_EXISTING):
            proj_name = self.project_enum[self.GetInt32(DRP_PROJ_NAME)]
        else:
            proj_name = self.GetString(TXT_PROJ_NAME)
        scene_name = self.GetString(TXT_SCENE_NAME)
        prod_folder = database.getProduction(prod_name)['project']
        # Don't allow spaces as the user types
        proj_name = proj_name.replace(' ', '_') 
        scene_name = scene_name.replace(' ', '_')
        self.SetString(TXT_PROJ_NAME, proj_name)
        self.SetString(TXT_SCENE_NAME, scene_name)
        # Generate preview paths
        scene_prev = '{}_{}.c4d'.format(proj_name, scene_name)
        proj_prev  = os.path.relpath(
            "{}\\{}\\c4d\\".format(prod_folder, proj_name),
            "\\\\cagenas\\workspace\\MASTER_PROJECTS\\"
            )
        self.SetString(TXT_PREVIEW_PROJ, proj_prev)
        self.SetString(TXT_PREVIEW_FILE, scene_prev)

    def refreshProductionChange(self):
        if not (self.GetInt32(DRP_PROD_NAME) == 0):
            self.productionSelected(True)
            self.pullProjectList()
            self.refresh()

    def productionSelected(self, bool_):
        self.Enable(CHK_EXISTING, bool_)
        self.Enable(DRP_PROJ_NAME, bool_)
        self.Enable(TXT_PROJ_NAME, bool_)
        self.Enable(TXT_SCENE_NAME, bool_)
        self.Enable(RDO_FRAMERATE, bool_)
        if (bool_ == True):
            chk = self.GetBool(CHK_EXISTING)
            self.Enable(DRP_PROJ_NAME, chk)
            self.Enable(TXT_PROJ_NAME, 1-chk)

    def pullProductionList(self):
        # generate a dictionary with gui ID as key and name as value
        id_ = DRP_PROD_NAME_START_ID
        for prod in database.getAllProductions():
            self.production_enum[id_] = prod
            self.production_ids.append(id_)
            id_ += 1
        # populate production list
        for prod in self.production_enum:
            self.AddChild(DRP_PROD_NAME, prod, self.production_enum[prod])

    def pullProjectList(self):
        # generate a dictionary with gui ID as key and name as value
        id_ = DRP_PROJ_NAME_START_ID
        for proj in database.getAllProjects(self.production_enum[self.GetInt32(DRP_PROD_NAME)]):
            self.project_enum[id_] = proj
            self.project_ids.append(id_)
            id_ += 1
        # populate project list
        for proj in self.project_enum:
            self.AddChild(DRP_PROJ_NAME, proj, self.project_enum[proj])

    def populateExistingScene(self):
        doc = c4d.documents.GetActiveDocument()
        fps = doc.GetFps()
        
        for k,v in self.production_enum.iteritems():
            if (v == self.this_scene.production):
                prod_id = k

        self.SetInt32(DRP_PROD_NAME, prod_id)
        self.refreshProductionChange()
        self.SetBool(CHK_EXISTING, True)

        for k,v in self.project_enum.iteritems():
            if (v == self.this_scene.project_name):
                proj_id = k

        self.SetInt32(DRP_PROJ_NAME, proj_id)
        self.Enable(TXT_PROJ_NAME, False)

        self.SetString(TXT_SCENE_NAME, self.this_scene.scene_name)
        self.SetInt32(RDO_FRAMERATE, 10000+fps)

        self.refresh()

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
    fn = os.path.join(dir, "res", "icon.tif")
    bmp.InitWith(fn)

    #desc = plugins.GeLoadString(ESPNPipelineMenu)

    plugins.RegisterCommandPlugin(id=PLUGIN_ID,
                                  str="ESPN Pipeline",
                                  info=0,
                                  help="Main menu for ESPN pipeline operations",
                                  dat=ESPNPipelinePlugin(),
                                  icon=bmp)