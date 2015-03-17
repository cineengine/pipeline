# Built-in modules
import pymel.core as pm

# Internal modules
from pipeline import cfb
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
    pm.mel.eval('renderThumbnailUpdate true;')

    asset.reference(cfb.FACTORY_LIGHT_RIG, 'FACTORY')
    sorter = sort.SortControl('Factory')
    sorter.run()
