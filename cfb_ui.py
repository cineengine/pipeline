# Pymel (Maya commands module)
import pymel.core as pm

# Internal modules
from pipeline.maya import asset
from pipeline.maya import sort
import pipeline.maya.vray.utils as vrayutils
import pipeline.maya.vray.mattes as vraymattes

# Other ESPN modules
import cg.maya.rendering as rendering
import cg.maya.selection as selection

# CFB global variables
import pipeline.cfb as cfb

main_width = 123
emphasis = [0.1,0.38,0.52]
deemphasis = [0.27,0.27,0.27]
shinybtn = [.17,.83,.36]

def __init__(*a):
    pass

def run( *args ):
    ''' Widget for pipeline utilities '''
    if pm.window('pipeline', query=True, exists=True):
        pm.deleteUI('pipeline')

    pipeUI = pm.window( 'pipeline', title='pipeline', iconName='pipe', tlb=True, rtf=True, s=False, w=main_width )

    _mainmr = pm.columnLayout( adjustableColumn=False, w=main_width )

    #############################################################################################
    ## Tools
    #############################################################################################
    frame = pm.frameLayout(l='Tools', fn='smallBoldLabelFont', w=main_width, mh=5, bv=True, ebg=True, cll=True, cl=False, parent=_mainmr)

    grid = pm.gridLayout( nc=1, cellWidthHeight=(120,25))
    meshes_btn = pm.button( l="Select Meshes",
                            c=lambda *args: selection.shapes( pm.ls(sl=True), xf=True, do=True ),
                            ann="Convert your selection to geometry-level transforms only.",
                            p=grid )
    shaders_btn = pm.button( l="Select Shader",
                             c=lambda *args: rendering.getShader(select_result=True),
                             ann="Selects the shader assigned to your current selection.",
                             p=grid )     
    group_under_btn = pm.button( l="Make offset group",
                                 c=lambda *args: selection.createOffsetGrp( pm.ls(sl=True) ),
                                 h=25,
                                 ann='Copy the selection\'s transform matrix to a group and parent the selection under it.',
                                 p=grid )    
    pm.setParent('..')

    grid = pm.gridLayout( nc=1, cellWidthHeight=(120,20))
    lookup_btn = pm.button( l="Lookup Tricode",
                            c=lookupTricode,
                            ann="Lookup a team's tricode",
                            p=grid,
                            bgc=deemphasis
                            )
    pm.setParent('..')


    #################################################################################
    #################################################################################
    #### ASSETS #####################################################################
    #################################################################################
    #################################################################################
    
    frame = pm.frameLayout(l='Assets', fn='smallBoldLabelFont', w=main_width, mh=5, bv=True, ebg=True, cll=True, cl=False, parent=_mainmr)

    row = pm.rowLayout( nc=2, p=frame)
    lbl = pm.text( l="Creation:", align='center', fn='smallPlainLabelFont', p=row )
    pm.setParent('..')    

    grid = pm.gridLayout( nc=1, cellWidthHeight=(120,25))
    #factory_btn = pm.button( l="Build Factory Scene",
    #                         w=120, h=25,
    #                         bgc=emphasis,
    #                         c=build.factory
    #                         )
    

    make_new_btn = pm.button( l="Make New Asset",
                              w=120, h=25,
                              bgc=emphasis,
                              c=asset.makeNew 
                              )
    pm.setParent('..')

    grid = pm.gridLayout( nc=1, cellWidthHeight=(120,15))
    #sort_f_btn = pm.button( l="Sort Factory Scene",
    #                        w=120, h=15,
    #                        c=lambda *args: sort.sceneFromDb(cfb.db.SortDict('Factory'))
    #                        )
    pm.setParent('..')

    #grid = pm.gridLayout( nc=1, cellWidthHeight=(120,20))
    #sort_f_btn = pm.button( l="Sort into Factory",
                            #w=60, h=20,
                            #bgc=deemphasis,
                            #c=lambda *args: sort.sceneFromDb(SortDict('Factory'))
    pm.setParent('..')
    
    #################################################################################
    #### V-RAY STUFF ################################################################
    #################################################################################

    row = pm.rowLayout( nc=2, p=frame)
    lbl = pm.text( l="Sorting groups:", align='center', fn='smallPlainLabelFont', p=row )
    pm.setParent('..')

    grid = pm.gridLayout( nc=1, cellWidthHeight=(120,25))
    #BUTTON - VRay Object Properties
    make_object_properties_btn = pm.button( l = 'Geometry Sort Set',
                                            bgc = emphasis,
                                            c = vrayutils.makeObjectProperties,
                                            ann = 'Make a V-Ray object properties group.',
                                            p=grid )
    pm.popupMenu()
    append_geo_menu = pm.menuItem(l='Add to existing ...', c=lambda *args: vrayutils.addToSet( typ='geo' ) )
    

    #BUTTON - VRay Light Properties
    make_light_set_btn = pm.button( l = 'Light Sort Set',
                                    bgc = emphasis,
                                    c = vrayutils.makeLightSelectSet,
                                    ann = 'Make a V-Ray light select set.')
    pm.popupMenu()
    append_lgt_menu = pm.menuItem(l='Add to existing ...', c=lambda *args: vrayutils.addToSet( typ='lgt' ) )

    
    #BUTTON - Open mattes widget
    matte_assign_ui_btn = pm.button( l = 'V-Ray Mattes',
    				     bgc = emphasis,
    			             c = vraymattes.run,
    			             ann = 'Open the matte assignment utility window')   
    
    pm.setParent('..')

    #################################################################################
    ### ASSET CHECK-IN ##############################################################
    #################################################################################
    
    row = pm.rowLayout( nc=1, w=main_width, p=frame)
    lbl = pm.text( l="Check-in:", align='center', fn='smallPlainLabelFont')
    pm.setParent('..')    
    
    grid = pm.gridLayout( nc=2, cellWidthHeight=(60,33))    
    check_btn = pm.button( l="Chk Model",
                           w=120, h=25,
                           c=lambda *args: asset.sanityCheck(report=True, model=True)
                           )
    check_btn = pm.button( l="Chk Mats",
                           w=120, h=25,
                           c=lambda *args: asset.sanityCheck(report=True, shading=True)
                           )
    pm.setParent('..')



    grid = pm.gridLayout( nc=1, cellWidthHeight=(120,60))
    export_btn = pm.button( l="Export Asset",
                            w=60, h=33,
                            bgc=shinybtn,
                            c=asset.export
                            )
    pm.setParent('..')
    
    grid = pm.gridLayout( nc=1, cellWidthHeight=(120,20))
    ref_btn = pm.button( l="Reference Asset",
                            w=60, h=20,
                            bgc=deemphasis,
                            c=lambda *args: assetSelector(init=True, mode='reference')
                            )
    import_btn = pm.button( l="Import Asset",
                            w=60, h=20,
                            bgc=deemphasis,
                            c=lambda *args: assetSelector(init=True, mode='import')
                            )
    swap_ref_btn = pm.button( l="Remove and reference",
                            w=60, h=20,
                            bgc=[0.63,0.17,0.17],
                            c=asset.swapImportWithReference
                            )
    swap_imp_btn = pm.button( l="Remove and import",
                            w=60, h=20,
                            bgc=[0.63,0.17,0.17],
                            c=asset.swapReferenceWithImport
                            )

    pm.setParent('..')    



    """
    # ###########################################################################################
    # Templates
    # ###########################################################################################
    frame = pm.frameLayout(l='Templates', fn='smallBoldLabelFont', w=123, mh=5, bv=True, ebg=True, cll=True, cl=False, parent=_mainmr)

    grid = pm.gridLayout( nc=1, cellWidthHeight=(120,25))
    build_btn = pm.button( l="Build Scene",
                              w=120, h=25,
                              c=lambda *args: pm.Mel.eval('HypershadeWindow;')
                              )
    make_btn = pm.button( l="Save New Template",
                           w=120, h=25,
                           c=lambda *args: pm.Mel.eval('TextureViewWindow;')
                           )
    pm.setParent('..')
    """

    #dock = pm.dockControl( 'pipelineDock', label='pipeline', area='left', content=pipeUI, allowedArea=allowedAreas)
    pipeUI.show()
    
def assetSelector( init=None, mode='reference', *a):
    
    def _get( *a ):
        return pm.textScrollList( 'sel_box', q=True, selectItem=True )[0]
    

    def _run( mode, typ, *a ):
        if typ == 'generic':
            folder = cfb.MAIN_ASSET_DIR
        elif typ == 'team':
            folder = cfb.TEAMS_ASSET_DIR
        elif typ == 'template':
            folder = cfb.TEMPLATE_DIR

        asset_name = _get()
        
        if mode == 'reference':
            asset.reference(get_file = (folder + asset_name + "\\" + asset_name + ".mb"))
        elif mode == 'import':
            asset.importAsset(get_file = (folder + asset_name + "\\" + asset_name + ".mb"))
    

    if init == True:    
        init = pm.confirmDialog( title='Select asset type:',
                                     message='What type of asset?',
                                     button=['Generic','Team','Template'],
                                     defaultButton='Generic',
                                     dismissString='Cancel'
                                     )

    if init == 'Cancel':
        return False    
    
    try:
        pm.deleteUI('select_win')
    except: pass
    
    select_win = pm.window( 'select_win',
                            title='Select asset:',
                            tlb=True, rtf=True, s=False,
                            width=150
                            )
    
    # Basic window layout
    top = pm.formLayout(p=select_win)
    sel_box = pm.textScrollList('sel_box', p=top, dcc=lambda *args: _run(mode,init.lower()))
    get_btn = pm.button('get_btn',
                        label='Select',
                        c=lambda *args: _run(mode,init.lower()),
                        h=25)
    top.redistribute(3.336,1)
    
    # Get the list of assets specified in init_win    
    asset_list = asset.getAssetList(typ=init.lower())

    sel_list = pm.textScrollList( 'sel_box',
                                  e=True,
                                  append=asset_list,
                                  numberOfRows=min(25, max(10, len(asset_list)))
                                  )
   
    select_win.show()
    
def referenceSelector(*a):

    def _run(*a):
        # Get target namespace & asset file from UI
        sel      = pm.textScrollList('selectNamespace', q=True, si=True)[0]
        get_file = pm.fileDialog2(dir=cfb.MAIN_ASSET_DIR, ds=1, fm=1)[0]

        asset.reference(get_file, sel)

    # UI for namespace selection
    try: pm.deleteUI('refAsset')
    except: pass
    widget = pm.window(
                'refAsset',
                title='Reference Asset into Namespace',
                tlb=True,
                rtf=True
                )
    main = pm.formLayout(p=widget)
    label = pm.text(label='What namespace will this reference into?')
    ns_box = pm.textScrollList(
                'selectNamespace', 
                numberOfRows=10, 
                parent=main,
                ams=False, 
                append=cfb.NAMESPACES
                )
    rf_but = pm.button(l='Select Asset to Reference', p=main, c=_run)
    main.redistribute(1,5,3)
    widget.show()



class RenderTemplateWindow(pm.uitypes.Window):
    
    class TabBox(object):
        def __init__(self, layer, parent):
            self.name = str(layer)
            self.parent = parent
            self.sort_dict = {'light':'',
                              'beaut':'',
                              'bhole':'',
                              'pvoff':'',
                              'aovon':''}
        
        def make(self):
            tab_box = pm.verticalLayout(h=125, p=self.parent)
            self.light_field = pm.textFieldGrp( str(self.name)+'_light', cc=self.update_dict, label='Lights :', text='', p=tab_box )
            self.beaut_field = pm.textFieldGrp( str(self.name)+'_beaut', cc=self.update_dict, label='Beauty :', text='', p=tab_box )
            self.bhole_field = pm.textFieldGrp( str(self.name)+'_bhole', cc=self.update_dict, label='Black Hole :', text='', p=tab_box )
            self.pvoff_field = pm.textFieldGrp( str(self.name)+'_pvoff', cc=self.update_dict, label='Primary Visibility Off :', text='', p=tab_box )
            self.aovon_field = pm.textFieldGrp( str(self.name)+'_aovon', cc=self.update_dict, label='AOV Only (UTIL) :', text='', p=tab_box )
            tab_box.redistribute()           
            pm.setParent('..')
            
            self.layout = tab_box
            return self.layout
        
        def update_dict(self, *a):
            self.sort_dict['light'] = pm.textFieldGrp(str(self.name)+'_light', q=True, text=True)
            self.sort_dict['beaut'] = pm.textFieldGrp(str(self.name)+'_beaut', q=True, text=True)
            self.sort_dict['bhole'] = pm.textFieldGrp(str(self.name)+'_bhole', q=True, text=True)
            self.sort_dict['pvoff'] = pm.textFieldGrp(str(self.name)+'_pvoff', q=True, text=True)
            self.sort_dict['aovon'] = pm.textFieldGrp(str(self.name)+'_aovon', q=True, text=True)
        
    def __init__(self):
        try:
            pm.deleteUI('renderTemplateMaker')
        except:
            pass
        
        #self.rename('renderTemplateMaker')        
        # Default settings inherited from pm.uitypes.Window
        self.setTitle('Render Template Maker')
        self.setToolbox()
        self.setResizeToFitChildren(1)        
        self.setSizeable(0)
        self.setWidth(400)
        self.setHeight(205)
        # The main dictionary, storing the contents of the current sorting assignments
        self.out_dict = {}
        # A list of all the TabBox / layer dictionary container objects
        self.all_tabs = []
        self.run()
        
    def run(self):
        # Main window definition
        self.main = pm.formLayout(p=self)
        self.top = pm.formLayout()

        
        # Dynamic tabs area definition
        self.tabs = pm.tabLayout('_tabs_')
        pm.formLayout(self.top,
                      edit=True,
                      attachForm=(
                          (self.tabs,'top',0),
                          (self.tabs,'left',0),
                          (self.tabs,'bottom',0),
                          (self.tabs,'right',0)),
                      p=self.top)
        
        # Define dummy box (instructions) for first run
        self.dummy_box = pm.verticalLayout(h=125, w=390)
        pm.text(l="Hi hi hi hi hi")
        pm.setParent('..')
        # Rename dummy box tab
        pm.tabLayout(self.tabs,
                      edit=True,
                      tl=(self.dummy_box, 'Instructions'))                
        
        # Button section (static)
        buttons = pm.horizontalLayout(p=self.top)
        make_btn = pm.button(label='Make New Layer', c=self.addNewLayer)
        try_btn = pm.button(label='Try Sorting')
        clear_btn = pm.button(label='Delete Layer', c=self.deleteLayer)
        clear_grps_btn = pm.button(label='Clear Tabs')
        # Button distribution
        buttons.redistribute()
        
        # Main layout distribution
        self.top.redistribute(3,1)

        self.show()
        
    def addNewLayer(self, *a):
        prompt = pm.promptDialog(title='Layer Name?',
                               message='New Layer Name : ',
                               button=['OK','Cancel'],
                               defaultButton='OK',
                               cancelButton='Cancel',
                               dismissString='Cancel')
        if prompt == 'OK':
            name = pm.promptDialog(q=True, text=True)
        else: return False
        
        if not name == '':
            try:
                pm.deleteUI(self.dummy_box)
            except UnboundLocalError: pass
            except RuntimeError: pass
            
            # Check that the layer does not already exist in the scene
            try:
                exists = pm.PyNode(name)
                if exists:
                    pm.warning('Layer (or an object with that name) already exists.')
                    return False
            except: pass
            
            # Make the actual render layer
            rendering.makeLayer(name)
            
            # Make a tab for that layer
            layer = self.TabBox(name, self.tabs)
            layer.make()
            self.all_tabs.append(layer)
            pm.tabLayout(self.tabs,
                        edit=True,
                        tl=(layer.layout, layer.name))

    def deleteLayer(self, *a):
        cur_tab = pm.tabLayout(self.tabs,
                               q=True,
                               selectTab=True)
        tab_name = pm.tabLayout(self.tabs,
                                q=True,
                                tl=True)
        tab_index = pm.tabLayout(self.tabs,
                                 q=True,
                                 sti=True)      
        try:
            # Annoying hack.  If someone is trying to delete the last tab,
            # this flags the dummy_box for re-creation.
            if len(tab_name) == 1:
                make_dummy = True
            
            pm.delete(pm.PyNode(tab_name[tab_index-1]))
            pm.deleteUI(cur_tab, layout=True)
            
            if make_dummy:
                # Being lazy, this is copied and pasted from above
                self.dummy_box = pm.verticalLayout(h=125, w=390)
                pm.text(l="Hi hi hi hi hi")
                pm.setParent('..')
                # Rename dummy box tab
                pm.tabLayout(self.tabs,
                              edit=True,
                              tl=(self.dummy_box, 'Instructions'))       
            return True
        except:
            return False
        
        
        def sort(self, *a):
            self.scene_dict = {}
            for tab in self.all_tabs:
                self.scene_dict[tab.name] = tab.sort_dict
            
            # uh oh, need to write sort.sceneFromDict()
            
def renderTemplate(*a):
    try:
        pm.deleteUI('renderTemplateWindow')
    except:
        pass
    win = RenderTemplateWindow()
    win.rename('renderTemplateWindow')
    return win

def lookupTricode(*a):
    
    def _capitalize(string):
        spl = string.split()
        if len(spl) == 1:
            if all(x.isupper() for x in list(spl)):
                return string
            else: return string.capitalize()
        
        elif len(spl) > 1:
            
            new_string = ''
            for i in range(len(spl)):
                if all(x.isupper() for x in list(spl[i])):
                    new_string += spl[i]
                else:
                    new_string += spl[i].capitalize()
                
                if not i == (len(spl)-1):
                    new_string += ' '
                else:
                    pass
            return new_string
            
        
    def _lookup(*a):
        _team_in = pm.textFieldGrp(text, q=True, text=True)
        _team_in = _capitalize(_team_in)
        _team = cfb.db.Team(_team_in)
        
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
    lay = pm.verticalLayout(width = 250, p=win)
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

g_main = pm.getMelGlobal('string','$gMainWindow')

pm.setParent(g_main)
mmenu = pm.menu('cfbTools', l='CFB \'15', to=True)

pm.setParent(menu=True)
#pm.menuItem(l="Reload Scripts", c=lambda *args: pm.evalDeferred( "exec('reload(cfb) in globals()')", lp=True )
#pm.menuItem(divider=True)
pm.menuItem(l="Launch Widget", c=run)

pm.menuItem(divider=True)
pm.menuItem(l="Select Meshes in Group", c=lambda *args: selection.shapes( pm.ls(sl=True), xf=True, do=True ))
pm.menuItem(l="Select Shader on Selected", c=lambda *args: rendering.getShader(select_result=True))
pm.menuItem(l="Make Offset Group", c=lambda *args: selection.createOffsetGrp( pm.ls(sl=True) ))


#pm.menuItem(divider=True)
#pm.menuItem(subMenu=True, to=True, label="Assets")
#pm.menuItem(l="Build Factory Scene", c=build.factory)
#pm.menuItem(l="Sort Factory Scene", c=lambda *args: sort.sceneFromDb(cfb.db.SortDict("Factory")))
#pm.menuItem(l="Make New Asset", c=asset.makeNew)

pm.menuItem(divider=True)
pm.menuItem(l="Reference Asset", c=lambda *args: assetSelector(init=True, mode='reference'))
pm.menuItem(l="Import Asset", c=lambda *args: assetSelector(init=True, mode='import'))
pm.menuItem(l="Remove and Reference", c=asset.swapImportWithReference)
pm.menuItem(l="Remove and Import", c=asset.swapReferenceWithImport)

pm.menuItem(divider=True)
pm.menuItem(l="Geometry Sort Set", c=vrayutils.makeObjectProperties)
pm.menuItem(l="Light Sort Set", c=vrayutils.makeLightSelectSet)
pm.menuItem(l="Matte Selector", c=vraymattes.run)

pm.menuItem(divider=True)
pm.menuItem(l="Check Model", c=lambda *args: asset.sanityCheck(report=True, model=True))
pm.menuItem(l="Check Shading", c=lambda *args: asset.sanityCheck(report=True, shading=True))
pm.menuItem(l="EXPORT ASSET", c=lambda *args: asset.export)

pm.menuItem(divider=True, p=mmenu)
pm.menuItem(l="Lookup Tricode", c=lookupTricode, p=mmenu)