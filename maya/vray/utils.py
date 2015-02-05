import pymel.core as pm
import cg.maya.selection as select

########################
### SCENE MANAGEMENT ###
########################
def initVray( *args, **kwargs ):
    try: 
        pm.loadPlugin("vrayformaya.mll")
        pm.setAttr('defaultRenderGlobals.ren', 'vray', type='string')
        return True
    except:
        pm.warning("Could not initialize V-Ray for some reason")
        return False

def setVrayDefaults( *args ):
    try:
        #initVray()
        v_ray = pm.PyNode('vraySettings')
        globs = pm.PyNode('defaultRenderGlobals')
        v_ray.imageFormatStr.set('exr')
        v_ray.imgOpt_exr_compression.set(3)
        v_ray.vfbOn.set(1)
        globs.animation.set(1)
        v_ray.animBatchOnly.set(1)
        v_ray.ddisplac_maxSubdivs.set(10)
        v_ray.gi.set(1)
        v_ray.refractiveCaustics.set(0)
        v_ray.dmcs_adaptiveAmount.set(1)
        v_ray.dmcs_adaptiveThreshold.set(0.010)
        v_ray.dmcThreshold.set(0.005)
        v_ray.globopt_light_doDefaultLights.set(0)
        v_ray.cmap_gamma.set(2.2)
        v_ray.cmap_subpixelMapping.set(1)
        v_ray.cmap_adaptationOnly.set(1)
        v_ray.ddisplac_maxSubdivs.set(8)
        print 'Successfully loaded V-Ray quick setup.'
    except pm.MayaNodeError:
        pm.error('Looks like V-Ray might not have been loaded yet.')
        return False
    except pm.AttributeError:
        pm.error('Attribute missing in V-Ray quick setup batch.')
    finally:
        pass


#########################
### SETS & PARTITIONS ###
#########################

def makeObjectProperties( sel=None ):
    """ A Layer creation widget that includes custom layer attributes """
    
    def _getLast(): # stupid hacks.  (python does not return a string when using the vray command.)
        _filter = pm.itemFilter(byType='VRayObjectProperties')
        _list = pm.lsThroughFilter( _filter, sort='byTime', reverse=False)
        _result = _list[len(_list)-1]
        return _result

    go = pm.promptDialog(title='Create New Sort Group',
                       message='Enter Name:',
                       button=['OK', 'Cancel'],
                       tx='sg_',
                       defaultButton='OK',
                       cancelButton='Cancel',
                       dismissString='Cancel')
    if go == 'OK':

        name = pm.promptDialog( query=True, text=True ) # set name via a prompt
        
        if not sel:
            sel = pm.ls(sl=True) # store selection for later restorationg
            select.shapes(sel, xf=True, do=True) # convert selection to meshes only
        
        pm.Mel.eval('vray objectProperties add_single;') # make the obj properties group

        try:
            _sg = _getLast() # have to do it this way because python and v-ray don't always get along
            pm.rename( _sg, name )
            pm.select(sel) # restore original selection
            if _sg.nodeType() == 'VRayObjectProperties':
                return _sg
            else: return None
        except:
            pm.warning("You're required to have a selection in order to create a V-ray partition (no idea why).")
            return None

def makeLightSelectSet( sel=None ):
    try:
        lgt = select.shapes(sel, xf=True, do=True)
    except: pass
    
    _go = pm.promptDialog(title='New Light Group:',
                              message='Enter Name:',
                              button=['OK', 'Cancel'],
                              tx='lg_',
                              defaultButton='OK',
                              cancelButton='Cancel',
                              dismissString='Cancel')
    
    if _go == 'OK':
        name = pm.promptDialog( query=True, text=True )
        _lg = pm.PyNode(pm.Mel.eval('vrayAddRenderElement LightSelectElement;')) # make the light grou
        
        pm.rename(_lg, name)
        _lg.vray_name_lightselect.set(name)
    else: return None    
    
    if sel:
        for obj in sel:
            pm.sets(_lg, edit=True, forceElement=obj)

    return _lg

def addToSet( typ=None, *args ):
    """Add an object to a VRay parition or properties group"""

    def add_sel( *args ):

        # Query the UI scroll list for the name of the target properties group
        try: 
            grp = pm.PyNode( pm.textScrollList( 'listBox', q=True, si=True )[0] )
        except: 
            pm.error('No group selected to add to.')
        
        sel = pm.ls(sl=True)
        
        try: 
            pm.sets( grp, edit=True, forceElement=sel )
        except Exception,e: print e

        # Add the selection to that group
        pm.sets( grp, edit=True, forceElement=sel )

        pm.warning('Added scene selection to: ' + grp + '.')

        return True

    def add_new( typ ):
        
        sel = pm.ls(sl=True)
                
        # Make a new group of the specified type.  Includes UI refresh.
        if typ == 'geo':
            grp = makeObjectProperties( sel )
        elif typ == 'lgt':
            grp = makeLightSelectSet( sel )
        #elif typ == 'disp':
        if grp:
            pm.textScrollList( 'listBox', e=True, append=grp )
        else: pass

    # Initialize UI values based on type of properties group specified.
    if typ == 'geo':
        title = 'obj properties grp:'
        ams = False
        grps = pm.ls(typ='VRayObjectProperties')

    elif typ == 'lgt':
        title = 'light select set:'
        ams = True
        grps = pm.ls(typ='VRayRenderElementSet')

    elif typ == 'disp':
        title = 'displacement grp:'
        ams = False
        grps = pm.ls(typ='VRayDisplacement')

    else:
        pm.error('appendToGroup(): \'typ\' flag not specified.')

    # Maya UI
    try: pm.deleteUI( 'selGrpWin' )
    except: pass

    selGrpWin = pm.window( 'selGrpWin', title=title, width=150, tlc=(800,85), rtf=True, tlb=True, s=False )
    winBox = pm.formLayout( width=150 )
    listBox = pm.textScrollList( 'listBox', append=grps, numberOfRows=min(20, len(grps)+5), fn='smallFixedWidthFont', width=150, ams=ams, p=winBox )
    #
    add_btn = pm.button( 'add_btn', l="- add to selected -", c=add_sel, width=148, height=25, p=winBox )
    #
    make_btn = pm.button( 'make_btn', l="- make new -", c=lambda *args: add_new( typ ), width=148, height=25, p=winBox )
    #
    winBox.redistribute(0,0)
    pm.showWindow( selGrpWin )

