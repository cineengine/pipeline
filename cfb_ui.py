# Pymel (Maya commands module)
import pymel.core as pm

# External modules
from pipeline.maya import asset
from pipeline.maya import sort
from pipeline.maya import build
from pipeline.maya import project
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
reload(team)
reload(vrayutils)
reload(vraymattes)
reload(rendering)
reload(selection)
reload(cfb)

main_width = 123
emphasis = [0.1,0.38,0.52]
deemphasis = [0.27,0.27,0.27]
shinybtn = [.17,.83,.36]

    
def lookupTricode(*a):
    
    def _lookup(*a):
        _team = team.Team(cfb.TEAM_DATABASE, pm.textFieldGrp(text, q=True, text=True))
        
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



### MAIN MENU

try:
    pm.deleteUI('cfbTools')
except: pass
try:
    pm.deleteUI('pipeline')
except: pass

scene = project.SceneManager(delay_init=True)

g_main = pm.getMelGlobal('string','$gMainWindow')

pm.setParent(g_main)
mmenu = pm.menu('cfbTools', l='CFB \'15', to=True)

pm.setParent(menu=True)
#pm.menuItem(l="Reload Scripts", c=lambda *args: pm.evalDeferred( "exec('reload(cfb) in globals()')", lp=True )
#pm.menuItem(divider=True)
#pm.menuItem(l="Launch Widget", c=run)

#pm.menuItem(divider=True)
pm.menuItem(l="Scene Setup", c=scene.initCheck)
pm.menuItem(l="Open Scene", c=scene.open)
pm.menuItem(l="Save Scene", c=scene.save)


pm.menuItem(divider=True)
pm.menuItem(l="Select Meshes in Group", c=lambda *args: selection.shapes( pm.ls(sl=True), xf=True, do=True ))
pm.menuItem(l="Select Shader on Selected", c=lambda *args: rendering.getShader(select_result=True))
pm.menuItem(l="Make Offset Group", c=lambda *args: selection.createOffsetGrp( pm.ls(sl=True) ))

pm.menuItem(divider=True)
#pm.menuItem(subMenu=True, to=True, label="Assets")
pm.menuItem(l="Build Factory Scene", c=lambda *args: build.factory())
#pm.menuItem(l="Sort Factory Scene", c=sort.factory)

pm.menuItem(divider=True)
pm.menuItem(l="Make New Asset", c=asset.makeNew)
pm.menuItem(l="Check Model", c=lambda *args: asset.sanityCheck(report=True, model=True))
pm.menuItem(l="Check Shading", c=lambda *args: asset.sanityCheck(report=True, shading=True))
pm.menuItem(l="EXPORT ASSET", c=asset.export)

pm.menuItem(divider=True)
pm.menuItem(l="Reference Asset", c=lambda *args: asset.assetSelector(init=True, mode='reference'))
pm.menuItem(l="Import Asset", c=lambda *args: asset.assetSelector(init=True, mode='import'))
pm.menuItem(l="Remove and Reference", c=asset.swapImportWithReference)
pm.menuItem(l="Remove and Import", c=asset.swapReferenceWithImport)

pm.menuItem(divider=True)
pm.menuItem(l="Geometry Sort Set / Obj Properties Grp", c=vrayutils.makeObjectProperties)
pm.menuItem(l="Light Sort Set / Select Set", c=vrayutils.makeLightSelectSet)
pm.menuItem(l="Matte Selector", c=vraymattes.run)

pm.menuItem(divider=True, p=mmenu)
pm.menuItem(l="Lookup Tricode", c=lookupTricode, p=mmenu)


