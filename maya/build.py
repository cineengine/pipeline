# Built-in modules
import pymel.core as pm

# Internal modules
from pipeline import cfb
from pipeline.maya import asset
from pipeline.maya import sort
from pipeline.maya import project

from pipeline.database import team
import pipeline.vray.utils as utils


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


def loadAssets(home_team, away_team=False, clean=True):
    # Check for attachment locators
    try:
        home_loc = pm.PyNode('HOME_LOCATOR')
        if away_team:
            away_loc = pm.PyNode('AWAY_LOCATOR')
    except:
        pm.warning('Build Scene  ERROR Missing sign attachment locator.' )

    # Check for existing references
    for ref in pm.listReferences():
        if ref.namespace == 'HOMESIGN':
            homesign_exists = True

        elif ref.namespace == 'HOMELOGO':
            homelogo_exists = True

        elif (away_team) and ref.namespace == 'AWAYSIGN':
            awaysign_exists = True

        elif (away_team) and ref.namespace == 'AWAYLOGO':
            awaylogo_exists = True

    # Instance team objects
    home = team.Team(home_team)
    if away_team: away = team.Team(away_team)

    # Create paths for signs / team logo scenes
    home

    # If existing
            # If dirty, replace
            # If clean, remove and reattach

    # If not existing
            # Reference and attach


def checkLoaded(matchup=False):

