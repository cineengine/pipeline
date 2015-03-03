import pymel.core as pm

# CFB modules
from pipeline import cfb

# Internal modules
#from pipeline.db import Team
#import pipeline.vray.renderElements as renderElements
#import pipeline.vray.mattes as mattes
#import cg.maya.rendering as rendering
from pipeline.maya import asset
from pipeline.maya import sort
from pipeline.maya import project

import pipeline.vray.utils as utils

def factory( *a ):
    ## INITIALIZE V-RAY SETTINGS
    pm.Mel.eval('unifiedRenderGlobalsWindow;')
    try:
        utils.initVray()
        utils.setVrayDefaults()
    except:
        pm.warning('V-Ray wasn\'t loaded. Try the command again')
        return None
    
    v_ray = pm.PyNode('vraySettings')
    v_ray.cam_overrideEnvtex.set(1)
    pm.mel.eval('renderThumbnailUpdate false;')

    asset.reference(cfb.FACTORY_LIGHT_RIG, 'FACTORY')
    sorter = sort.SortControl(cfb.SORTING_DATABASE, 'Factory', cfb.FRAMEBUFFERS)
    sorter.run()

def factory_old( factory_scene ):
    
    ## INITIALIZE V-RAY SETTINGS
    pm.Mel.eval('unifiedRenderGlobalsWindow;')
    try:
        utils.initVray()
        utils.setVrayDefaults()
    except:
        pm.warning('V-Ray wasn\'t loaded. Try the command again')
        return None
    
    v_ray = pm.PyNode('vraySettings')
    v_ray.cam_overrideEnvtex.set(1)
    pm.mel.eval('renderThumbnailUpdate false;')

    # REFERENCE FACTORY ELEMENTS
    # reference light rig
    asset.reference(factory_scene, 'FACTORY')
    # build framebuffers
    # get sorting template from DB
    sorter = sort.SortControl('Factory')
    # sort scene
    sorter.run()
    
    ## MAKE FACTORY LAYERS
    # Make the layers at the correct bit depths
    #layers( cfb.FACTORY_LAYERS )

    # CONNECT DIFFERENT HDRS
    # REDUNDANT SECOND LOOP: OH WELL
    for layer in rendering.getAllLayers():
        # Prepare Environment / HDR attributes for overriding
        pm.editRenderLayerGlobals(crl=layer)
        rendering.enableOverride(v_ray.cam_envtexBg)
        rendering.enableOverride(v_ray.cam_envtexGi)
        rendering.enableOverride(v_ray.cam_envtexReflect)
              
        # Add the light rigs / HDRs to the layer
        if str(layer) == 'NOON':
            pm.PyNode('FACTORY:HDR_NOON').outColor >> v_ray.cam_envtexBg
            pm.PyNode('FACTORY:HDR_NOON').outColor >> v_ray.cam_envtexGi
            pm.PyNode('FACTORY:HDR_NOON').outColor >> v_ray.cam_envtexReflect

        elif str(layer) == 'SUNSET':
            pm.PyNode('FACTORY:HDR_SUNSET').outColor >> v_ray.cam_envtexBg
            pm.PyNode('FACTORY:HDR_SUNSET').outColor >> v_ray.cam_envtexGi
            pm.PyNode('FACTORY:HDR_SUNSET').outColor >> v_ray.cam_envtexReflect

        elif str(layer) == 'NIGHT':
            pm.PyNode('FACTORY:HDR_NIGHT').outColor >> v_ray.cam_envtexBg
            pm.PyNode('FACTORY:HDR_NIGHT').outColor >> v_ray.cam_envtexGi
            pm.PyNode('FACTORY:HDR_NIGHT').outColor >> v_ray.cam_envtexReflect           

        elif str(layer) == 'STUDIO':
            pm.PyNode('FACTORY:HDR_STUDIO').outColor >> v_ray.cam_envtexBg
            pm.PyNode('FACTORY:HDR_STUDIO').outColor >> v_ray.cam_envtexGi
            pm.PyNode('FACTORY:HDR_STUDIO').outColor >> v_ray.cam_envtexReflect    

        else: pass
