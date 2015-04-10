# Pymel (Maya commands module)
import pymel.core as pm

# External modules
from pipeline.maya import asset
from pipeline.maya import sort
from pipeline.maya import build
from pipeline.maya import project
from pipeline.maya import anim
from pipeline.database import team

import pipeline.vray.utils as vrayutils
import pipeline.vray.mattes as vraymattes

# Other ESPN modules
import cg.maya.rendering as rendering
import cg.maya.selection as selection

# CFB global variables
import pipeline.cfb as cfb

reload(asset)
reload(sort)
reload(build)
reload(project)
reload(anim)
reload(team)
reload(vrayutils)
reload(vraymattes)
reload(rendering)
reload(selection)
reload(cfb)


######################################################################
# TRICODE LOOKUP
######################################################################

def lookupTricode(*a):
    
    def _lookup(*a):
        _team = team.Team(pm.textFieldGrp(text, q=True, text=True))
        
        try:
            _tri = _team.tricode
        except AttributeError:
            _tri = None
            
        if _tri:
            pm.text(tri, edit=True, label='         Tricode :  ' + str(_team.tricode))
            pm.colorSliderGrp( color_pri, edit=True, rgb=rendering.convertColor(_team.primary) )
            pm.colorSliderGrp( color_sec, edit=True, rgb=rendering.convertColor(_team.secondary) )
        else:
            pm.text(tri, edit=True, label='         Tricode :  NOT FOUND')
    
    try:
        pm.deleteUI('lookupTricode')
    except:
        pass
    
    win = pm.window('lookupTricode',
                    tlb=True, rtf=True, s=False,
                    title = 'Lookup Team Tricode'
                    )
    lay = pm.verticalLayout(width = 200, p=win)
    text = pm.textFieldGrp( label='Team Name : ', p=lay, cw2=(70,130), cc=_lookup)
    tri = pm.text(label='         Tricode : ', p=lay, align='left')
    color_pri = pm.colorSliderGrp( label='Primary : ', rgb=(0,0,0), cw3=(70,130,0) )
    color_sec = pm.colorSliderGrp( label='Secondary : ', rgb=(0,0,0), cw3=(70,130,0) )
    lay.redistribute()
    
    win.show()


######################################################################
# SORT CONTROL / TEAM SWITCHER
######################################################################

class SortControlLayout(pm.uitypes.Window):

    def __init__(self):

        self.wh = (280,160)
        self.setTitle('Scene Sort Controller')
        self.setToolbox()
        self.setResizeToFitChildren(1)
        self.setSizeable(1)
        self.setWidth(self.wh[0])
        self.setHeight(self.wh[1])
        #self.run()
        self.element_list = []

        with open("F:\\10_GITHUB\\pipeline\\database\\cfb_sorting.yaml") as yaml_stream:
            self.stream = yaml.load_all(yaml_stream)
            for element in self.stream:
                self.element_list.append(element['ELEMENT'])

      
        top_layout      = pm.formLayout(p=self)

        # selection box
        column          = pm.formLayout(p=top_layout)
        pm.text(label='Select elements to sort', font='tinyBoldLabelFont', p=column)
        self.sel_box    = pm.textScrollList('sel_box', p=column)
        pm.textScrollList('sel_box',
            e=True,
            ams=True,
            append=self.element_list,
            numberOfRows=min(25, max(10, len(self.element_list)))
            )
        column.redistribute(1,5)
        
        # buttons
        column          = pm.formLayout(p=top_layout)
        self.sort_btn   = pm.button(l='SORT SCENE', p=column)
        self.open_btn   = pm.button(l='Open Scene', p=column)
        self.save_btn   = pm.button(l='Save Scene', p=column)
        self.rename_btn = pm.button(l='Rename Scene', p=column)
        self.ref_btn    = pm.button(l='Reference Editor', p=column)
        column.redistribute(3,1,1,1)

        top_layout.redistribute()

        #self.show()

def sortControlWidget(*a):
    s = SortControlWidget()
    
    if pm.dockControl('sortingDock', query=True, exists=True):
        pm.deleteUI('sortingDock')
    
    allowedAreas = ['right', 'left']

    dock = pm.dockControl( 
        'sortingDock', 
        floating=True, 
        label='Sorting / Team Switching', 
        area='left', 
        content=s, 
        allowedArea=allowedAreas
        )



######################################################################
# MAIN MENU 
######################################################################

def save_ui(*a):
    if project.isScene():
        scene = project.Scene()
        scene.save()
    else: 
        return

def open_ui(*a):
    project.Scene.open()
    #scene.open()

def rename_ui(*a):
    if project.isScene():
        scene = project.Scene()    
        scene.rename()
    else:
        return

def init_scene(*a):
    scene = project.Scene()

try:
    pm.deleteUI('cfbTools')
except: pass
try:
    pm.deleteUI('pipeline')
except: pass

scene = project.Scene(delay=True)

g_main = pm.getMelGlobal('string','$gMainWindow')

pm.setParent(g_main)
mmenu = pm.menu('cfbTools', l='CFB \'15', to=True)

pm.setParent(menu=True)
#pm.menuItem(l="Reload Scripts", c=lambda *args: pm.evalDeferred( "exec('reload(cfb) in globals()')", lp=True )
#pm.menuItem(divider=True)
#pm.menuItem(l="Launch Widget", c=run)

#pm.menuItem(divider=True)

pm.menuItem(l="Open Scene", c=open_ui)
pm.menuItem(l="Save Scene", c=save_ui)
pm.menuItem(l="Rename Scene", c=rename_ui)

pm.menuItem(divider=True)
pm.menuItem(subMenu=True, to=True, l='General Utilities')
pm.menuItem(l="Select Meshes in Group", c=lambda *args: selection.shapes( pm.ls(sl=True), xf=True, do=True ))
pm.menuItem(l="Select Shader on Selected", c=lambda *args: rendering.getShader(select_result=True))
pm.menuItem(l="Make Offset Group", c=lambda *args: selection.createOffsetGrp( pm.ls(sl=True) ))
pm.menuItem(l="Lookup Tricode", c=lookupTricode, p=mmenu)
pm.setParent(mmenu, menu=True)

pm.menuItem(divider=True)
#pm.menuItem(subMenu=True, to=True, label="Assets")
pm.menuItem(l="Build Factory Scene", c=lambda *args: build.factory())
#pm.menuItem(l="Sort Factory Scene", c=sort.factory)

pm.menuItem(divider=True)
pm.menuItem(subMenu=True, to=True, l='Asset Creation')
pm.menuItem(l="Make New Asset", c=asset.makeNew)
pm.menuItem(divider=True)
pm.menuItem(l="Geometry Sort Group / V-Ray OPG", c=vrayutils.makeObjectProperties)
pm.menuItem(l="Light Sort Group / V-Ray LSS", c=vrayutils.makeLightSelectSet)
pm.menuItem(l="Matte Assignment", c=vraymattes.run)
pm.menuItem(divider=True)
pm.menuItem(l="Check Model", c=lambda *args: asset.sanityCheck(report=True, model=True))
pm.menuItem(l="Check Shading", c=lambda *args: asset.sanityCheck(report=True, shading=True))
pm.menuItem(divider=True)
pm.menuItem(l="EXPORT ASSET", c=asset.export)

pm.setParent(mmenu, menu=True)

pm.menuItem(divider=True)
pm.menuItem(subMenu=True, to=True, l='Scene Creation')
pm.menuItem(l="Scene Setup", c=init_scene)
pm.menuItem(l="Reference Asset", c=lambda *args: asset.assetSelector(init=True, mode='reference'))
pm.menuItem(l="Import Asset", c=lambda *args: asset.assetSelector(init=True, mode='import'))
pm.menuItem(l="Remove and Reference", c=asset.swapImportWithReference)
pm.menuItem(l="Remove and Import", c=asset.swapReferenceWithImport)
pm.setParent(mmenu, menu=True)

pm.menuItem(divider=True)
pm.menuItem(subMenu=True, to=True, l='Animation Tools')
pm.menuItem(l="Export Atom", c=anim.exportAtom)
pm.menuItem(l="Import Atom", c=anim.importAtom)
pm.menuItem(l="Export Camera", c=anim.exportCamera)
pm.menuItem(l="Import Camera", c=anim.importCamera)
pm.menuItem(l="Export Alembic", c=anim.exportAbc)

#pm.menuItem(divider=True)
#pm.menuItem(submenu=True, l='Rendering Setup')

#pm.menuItem(divider=True, p=mmenu)


