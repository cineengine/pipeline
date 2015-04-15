# Built-in modules
import pymel.core as pm

# Internal modules
from pipeline import cfb
from pipeline.maya import asset
from pipeline.maya import sort
from pipeline.maya import project

from pipeline.database.team import Team
import pipeline.vray.utils as utils

# Built-in modules
import os.path

def factory( *a ):
    ## INITIALIZE V-RAY SETTINGS
    pm.Mel.eval('unifiedRenderGlobalsWindow;')
    #try:
    utils.initVray()
    utils.setVrayDefaults()
    #except:
    #   pm.warning('V-Ray wasn\'t loaded. You may need to try the command again')
    #   return None
    

    v_ray = pm.PyNode('vraySettings')
    v_ray.cam_overrideEnvtex.set(1)
    pm.mel.eval('renderThumbnailUpdate true;')

    asset.reference(cfb.FACTORY_LIGHT_RIG, 'FACTORY')
    sc = sort.SortControl('Factory')
    sc.run()


def loadAssets(tricode, orientation, clean=True):

    orientation = orientation.upper()
    # Check for attachment locators
    try:
        scene_loc = pm.PyNode('{0}_LOCATOR'.format(orientation))
    except: 
        pm.warning('Build Scene  ERROR Missing sign attachment locator for {0} team.'.format(orientation))
        return

    # Get team info from database
    try:
        team = Team(tricode)
    except: 
        pm.warning('Build Scene  ERROR Could not find team in database.')
        return

    # Generate string for the name of the school's sign
    sign = 'SIGN_{0}'.format(team.sign.upper())

    # Create paths for signs / team logo scenes
    sign_path = os.path.join(cfb.MAIN_ASSET_DIR, sign, (sign+'.mb'))
    logo_path = os.path.join(cfb.TEAMS_ASSET_DIR, team.tricode, (team.tricode+'.mb'))

    # Check for existing references
    sign_ref, logo_ref = None

    for ref in pm.listReferences():
        if ref.namespace == '{0}SIGN'.format(orientation):
            sign_ref = ref

        elif ref.namespace == '{0}LOGO'.format(orientation):
            logo_ref = ref

    # If the user has asked to do a clean reference of the asset, including attachment
    if (clean):
        # If there's already references in those namespaces, just delete them
        if (logo_ref): logo_ref.remove()
        if (sign_ref): sign_ref.remove()
        # Reference in the asset to the namespace
        asset.reference(sign_path, '{0}SIGN'.format(orientation))
        asset.reference(logo_path, '{0}LOGO'.format(orientation))

        attachToSign(orientation)

    # (If) there is already a sign reference in the namespace, and the user is requesting
    # to replace the reference and maintain reference edits (dirty mode)
    elif (sign_ref) and not clean:
        # If the right sign is already loaded, pass
        if (sign) in sign_ref.path:
            pass
        # Or else replace the sign reference
        else:
            sign_ref.replaceWith(sign_path)

    # Still dirty mode, same steps, this time with logos
    elif (logo_ref) and not clean:
        if (team.tricode) in logo_ref.path:
            pass
        else:
            logo_ref.replaceWith(logo_path)


def attachToSign(orientation):
    orientation = orientation.upper()

    sign_namespace = '{0}SIGN'.format(orientation)
    logo_namespace = '{0}LOGO'.format(orientation)

    # Get basic attachment points
    try:
        sign_atch_board  = pm.PyNode('{0}:ATTACH_01'.format(sign_namespace))
        sign_atch_bldg   = pm.PyNode('{0}:ATTACH_05'.format(sign_namespace))
        sign_atch_mascot = pm.PyNode('{0}:ATTACH_06'.format(sign_namespace))

        logo_atch_board  = pm.PyNode('{0}:ATTACH_01'.format(logo_namespace))

    except:
        pm.warning('Build Scene  ERROR Critical attachment points not found for {0} team.'.format(orientation))
    
    # Get optional attachment points.  These do not exist in every element.
    try:
        logo_atch_bldg   = pm.PyNode('{0}:ATTACH_05'.format(logo_namespace))
    except: logo_atch_bldg = None
    try:
        sign_atch_mascot = pm.PyNode('{0}:ATTACH_06'.format(logo_namespace))
    except: logo_atch_mascot = None

    attach(sign_atch_board, logo_atch_board)
    if (logo_atch_bldg):
        attach(sign_atch_bldg, logo_atch_bldg)
    if (logo_atch_mascot):
        attach(sign_atch_mascot, logo_atch_mascot)    
    return


def attach(parent, child):
    pc = pm.parentConstraint(parent, child, mo=False)
    sc = pm.scaleConstraint(parent, child, mo=False)
    return (pc,sc)


