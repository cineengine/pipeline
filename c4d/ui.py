# !/usr/bin/python
# coding: UTF-8

#    UI module for Cinema 4d Python API
#    
#    Author:  Mark Rohrer
#    Contact: mark.rohrer@gmail.com
#    Version: 0.1
#    Date:    03/07/2016
#
#    This version represents core functionality.    
#
#    

# internal libraries
import c4d
from c4d import gui
# custom libraries
from pipeline.c4d import core
from pipeline.c4d import component
from pipeline.c4d import database


class ProjectInitWindow(gui.GeDialog):
    def __init__(self):
        self.LBL_SHOW_NAME    = 1000
        self.LBL_PROJECT_NAME = 1001
        self.LBL_SCENE_NAME   = 1002
        self.LBL_FRAMERATE    = 1003

        self.TXT_PROJECT_NAME = 2001
        self.TXT_SCENE_NAME   = 2002

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
        for proj in database.PRODUCTIONS:
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
            scene_ctrl = self.execute()
            self.Close()
        elif id == self.BTN_CANCEL:
            self.Close()
        return True


    @classmethod
    def makeSceneCtrl(self):
        ''' Makes a scene control node -- a null called '__SCENE__' '''
        doc = core.doc()
        scene_ctrl = c4d.BaseObject(c4d.Onull)
        doc.InsertObject(scene_ctrl)
        scene_ctrl.SetName('__SCENE__')
        scene_tag = component.tag(c4d.Tannotation, 'SCENE_DATA', scene_ctrl)[0]
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
        return scene_ctrl

