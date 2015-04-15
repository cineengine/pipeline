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

import yaml

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


blue = [0,0.38,0.52]
red  = [0.52,0,0]

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

        self.wh = (220,500)
        self.setTitle('Scene Controller')
        #self.setToolbox()
        self.setResizeToFitChildren(1)
        self.setSizeable(1)
        self.setHeight(self.wh[1])
        #self.setWidth(self.wh[0])
        self.element_list = []

        with open(cfb.SORTING_DATABASE) as yaml_stream:
            self.stream = yaml.load_all(yaml_stream)
            for element in self.stream:
                self.element_list.append(element['ELEMENT'])

        main = pm.columnLayout()

        # TEAM SWITCHING LAYOUT
        top_frame = pm.frameLayout(
            l='Team Switcher',
            #w=self.wh[0], 
            fn='smallBoldLabelFont',
            cll=True,
            cl=False,
            p=main
            )
        
        column = pm.formLayout(p=top_frame)
        matchup_tgl = pm.radioButtonGrp(
            'matchup_toggle',
            label='',
            labelArray2=['Single Team', 'Matchup'],
            numberOfRadioButtons=2,
            cw=[(1,0)],
            cl2=['left','left'],
            cc=self.toggleMatchup,
            p=column
            )
        matchup_tgl.setSelect(1)

        home_team_txt = pm.textFieldGrp(
            'home_team_txt',
            l='Home Team',
            cw2=[78,130],
            cl2=['right','right'],
            p=column
            )
            
        away_team_txt = pm.textFieldGrp(
            'away_team_txt',
            l='Away Team',
            cw2=[78,130],
            cl2=['right','right'],
            en=False,
            p=column
            )

        clean_tgl = pm.checkBox('clean_toggle')
        clean_tgl.setLabel('Clean')
        clean_tgl.setValue(1)


        switchteam_btn = pm.button(
            'switch_team',
            l='L O A D   T E A M',
            bgc=red,
            c=self.loadBtn,
            p=column
            )
            
        column.redistribute()

        # SCENE SORTING LAYOUT
        bot_frame = pm.frameLayout(
            l='Scene Sorting',
            w=self.wh[0], 
            fn='smallBoldLabelFont', 
            cll=True, 
            cl=False, 
            p=main
            )

        # selection box
        column          = pm.formLayout(
                            p=bot_frame, 
                            #width=(self.wh[0]-5),
                            )
        pm.text(label='Select elements to sort', align='left', font='tinyBoldLabelFont', p=column)
        self.sel_box    = pm.textScrollList('sel_box', p=column)
        pm.textScrollList('sel_box',
            e=True,
            ams=True,
            append=self.element_list,
            numberOfRows=15,
            p=column
            )
                    
        # buttons
        self.sort_btn   = pm.button(l='SORT SCENE', bgc=blue, p=column, c=self.sortBtn)
        self.teardn_btn = pm.button(l='TEARDOWN SCENE', p=column, c=self.teardownBtn)
        
        box             = pm.formLayout(p=column)
        grid_l          = pm.gridLayout(nc=2,nr=2,cr=True, cwh=((self.wh[0]/2)-3, 15), p=box)
        self.open_btn   = pm.button(l='Open Scene', c=open_ui, p=grid_l)
        self.save_btn   = pm.button(l='Save Scene', c=save_ui, p=grid_l)
        self.rename_btn = pm.button(l='Rename Scene', c=rename_ui, p=grid_l)
        self.ref_btn    = pm.button(
                            l='Reference Editor', 
                            c=lambda *args: pm.mel.eval('ReferenceEditor;'), 
                            p=grid_l
                            )
        
        column.redistribute(1,15,3,1,4)
        #main.redistribute(1,4)


    def sortBtn(self, *a):
        sel = pm.textScrollList(
                'sel_box',
                q=True,
                si=True
                )

        for s in sel:
            sc = sort.SortControl(s)
            sc.run()


    def loadBtn(self, *a):
        home_team = pm.textFieldGrp('home_team_txt', q=True, text=True)
        clean = pm.checkBox('clean_toggle', q=True, value=True)

        if home_team == '':
            pm.warning('Build Scene  ERROR Please enter a team name / tricode before proceeding.')

        if (pm.radioButtonGrp('matchup_toggle', q=True, sl=True)) == 1:
            build.loadTeams(home_team, clean=clean)

        elif (pm.radioButtonGrp('matchup_toggle', q=True, sl=True)) == 2:
            away_team = pm.textFieldGrp('away_team_txt', q=True, text=True)
            build.loadTeams(home_team, away_team, clean=clean)


    def teardownBtn(self, *a):
        sort.sceneTeardown()


    def toggleMatchup(self, *a):
        get_bool = pm.radioButtonGrp('matchup_toggle', q=True, sl=True)
        if get_bool == 1:
            pm.textFieldGrp('away_team_txt', e=True, enable=False)
        elif get_bool == 2:
            pm.textFieldGrp('away_team_txt', e=True, enable=True)
        else:
            pm.warning('SORT CONTROL  ERROR: Please select single-team or matchup.')
        return


def sortControlWidget(*a):
    s = SortControlLayout()
    
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
pm.menuItem(l="Sort Control / Load Team", c=sortControlWidget)
pm.menuItem(subMenu=True, to=True, l='Scene Setup')
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


