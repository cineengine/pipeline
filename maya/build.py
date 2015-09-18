# Internal modules
import pymel.core as pm

# External modules
from pipeline import cfb
from pipeline.maya import asset
from pipeline.maya import sort
from pipeline.maya import project
from pipeline.maya import submit

from pipeline.database.team import Team
import pipeline.vray.utils as utils

# Built-in modules
import os.path
import re

reload(cfb)
reload(asset)
reload(sort)
reload(project)
reload(submit)


##############################################################################
### CALLED FUNCTIONS #########################################################
##############################################################################

def quad(team, *a):
    ''' A full scene-building routine for 'quad' logo slicks '''
    loadTeamsLite(team, team)
    sorter = sort.SortControl('Quad')
    sorter.run()

    try:
        pm.PyNode('HOMELOGO:GEO_05').visibility.set(0)
        pm.PyNode('AWAYLOGO:GEO_05').visibility.set(0)
    except: pass
    try:
        pm.PyNode('HOMELOGO:GEO_06').visibility.set(0)
        pm.PyNode('AWAYLOGO:GEO_06').visibility.set(0)
    except: pass

    v_ray = pm.PyNode('vraySettings')
    v_ray.fileNamePrefix.set("""TEAMS/{0}/%l/%l.#""".format(team))

    scene = project.Scene()
    scene.rename(team)


def singleTeam(tricode, package):
    ''' A full scene-building routine for single-team elements.'''
    #load in the new team
    loadTeamsStadium(tricode, diagnostic=False, clean=True)
    #sort
    sort.sceneTeardown()
    sc = sort.SortControl('Single_Team_{}'.format(package.upper()))
    sc.run()
    #change output path
    vrs = pm.PyNode('vraySettings')
    vrs.fileNamePrefix.set('TEAMS/{}/%l/%l.#'.format(tricode)) 
    #rename / save scene
    scene = project.Scene()
    scene.rename(tricode)


def singleTeamCity(tricode):
    ''' A full scene-building routine for single-team CITY elements.'''
    loadTeamsLite(tricode)
    #sort
    sort.sceneTeardown()
    sc = sort.SortControl('Single_Team_CITY')
    sc.run()
    # change output path
    vrs = pm.PyNode('vraySettings')
    vrs.fileNamePrefix.set('TEAMS/{}/%l/%l.#'.format(tricode))
    # rename / save scene
    scene = project.Scene()
    scene.rename(tricode)


def splitMatchupCity(tricode):
    ''' A full scene-building routine for single-team CITY elements.'''
    loadTeamsLite(tricode, tricode)
    #sort
    sort.sceneTeardown()
    sc = sort.SortControl('Matchup_CITY')
    sc.run()
    # change output path
    vrs = pm.PyNode('vraySettings')
    vrs.fileNamePrefix.set('TEAMS/{}/%l/%l.#'.format(tricode))
    # rename / save scene
    scene = project.Scene()
    scene.rename(tricode)


def splitMatchup(tricode, package):
    ''' A full scene-building routine for single-team elements.'''
    #load in the new team
    loadTeamsStadium(tricode, tricode, diagnostic=False, clean=True)
    #sort
    sort.sceneTeardown()
    sc = sort.SortControl('Split_Matchup_{}'.format(package.upper()))
    sc.run()
    #change output path
    vrs = pm.PyNode('vraySettings')
    vrs.fileNamePrefix.set('TEAMS/{}/%l/%l.#'.format(tricode)) 
    #rename / save scene
    scene = project.Scene()
    scene.rename(tricode)


def updateTeamLogo(tricode):
    # Get list of skeleton scenes and iterate over them
    skeletons = [#('CFB_E_TEAM_FE_01_ST', 'single', '1-75'),
                 ('CFB_E_TEAM_ENDSTAMP_01_ST', 'single', 'stadium', '1-300'),
                 ('CFB_S_TEAM_FE_01', 'single', 'studio', '1-90'),
                 ('CFB_E_MATCHUP_FE_01_ST', 'split', 'stadium', '1-75'),
                 ('CFB_E_MATCHUP_ENDSTAMP_01_ST', 'split', 'jumbo', '1-300'),
                 #('CFB_S_MATCHUP_FE_01', 'split', '1-83'),
                 ('TEAM_LOGO_QUADS', 'quad', '1-2')
                ]
    
    report = ''
    flag = 0

    for skeleton in skeletons:
        deliverable, type_, package, frange = skeleton

        # generate path for skeleton scene
        file_name = deliverable + '_SKELETON' + '.mb'
        file_path = os.path.join(cfb.ANIMATION_PROJECT_DIR, deliverable, 'maya', 'scenes', file_name)

        if not os.path.exists(file_path):
            #print file_path
            flag = 1
            report += '\nWARNING could not find {}.'.format(deliverable)
            continue

        try:
            # open scene
            project.Scene.open(file_=file_path, force=True)
            # build scene with new logo, based on type
            if type_ == 'single':
                singleTeam(tricode, package)
            elif type_ == 'split':
                splitMatchup(tricode, package)
            elif type_ == 'quad':
                quad(tricode)
            ## submit to farm
            submit.autoSubmitAll(frange, '/C', '', '5000')
            ## append to report
            report += '\nSuccessfully modified & submitted {} update for {}'.format(deliverable, tricode)
        except:
            flag = 1
            report += '\nWARNING failed to update {} for {}'.format(deliverable, tricode)

    print report

    if not flag:
        pm.warning('Build Scene  Update team logo operation completed with no errors.  Check the farm for your submissions.')
    elif flag:
        pm.warning('Build Scene  ERROR updating team logo.  Check script editor for details.')



def cityWeeklyBuild(tricode_list):
    report = ''
    flag = 0
    # List order:  SNF - away, home; PT - away, home
    skeletons = [('CFB_E_TEAM_FE_02', 'single', '1-150'),
                 ('CFB_E_TEAM_ENDSTAMP_02', 'single', '1-600'),
                 ('CFB_E_MATCHUP_FE_02', 'split', '1-150'),
                 ('CFB_E_MATCHUP_ENDSTAMP_02', 'split', '1-600'),
                 ('CFB_E_B2B_03_C', 'split', '1-150'),
                 ('CFB_E_VIZ_BUMP_02', 'split', '1-150'),
                 ('CFB_E_OPEN_02_C_SH0010', 'split', '1-59'),
                 ('CFB_E_OPEN_02_C_SH0020', 'single', '1-60'),
                 ('CFB_E_OPEN_02_C_SH0050', 'single', '1-43'),
                 ('CFB_E_OPEN_02_C_SH0080', 'split', '1-130')
                 ]

    for tricode in tricode_list:
        for skeleton in skeletons:

            deliverable, type_, frange = skeleton

            file_name = deliverable + '_SKELETON.mb'
            file_path = os.path.join(cfb.ANIMATION_PROJECT_DIR, deliverable, 'maya', 'scenes', file_name)

            if not os.path.exists(file_path):
                flag = 1
                report += '\nWARNING could not find {}.'.format(deliverable)
                continue

            try:
                project.Scene.open(file_=file_path, force=True)
                if type_ == 'single':
                    singleTeamCity(tricode)
                elif type_ == 'split':
                    splitMatchupCity(tricode)
                submit.autoSubmitAll(frange, '/C', '', '5000')
                report += '\nSuccessfully modified & submitted {} update for {}'.format(deliverable, tricode)
            except:
                flag = 1
                report += '\nWARNING failed to update {} for {}'.format(deliverable, tricode)

    print report

    if not flag:
        pm.warning('Build Scene  Update team logo operation completed with no errors.  Check the farm for your submissions.')
    elif flag:
        pm.warning('Build Scene  ERROR updating team logo.  Check script editor for details.')



def factory( *a ):
    asset.reference(cfb.FACTORY_LIGHT_RIG, 'FACTORY')
    sc = sort.SortControl('Factory')
    sc.run()


##############################################################################
### LOW-LEVEL FUNCTIONS  #####################################################
##############################################################################

def attachTeamLite(location):
    ''' Attaches a team logo to a locator called {LOCATION}_LOCATOR.'''
    location = location.upper()

    logo_namespace = '{0}LOGO'.format(location)

    logo_atch = None
    try:
        logo_atch = pm.PyNode('{0}LOGO:ATTACH_01'.format(location))
    except:
        pm.warning('Build Scene  ERROR Could not find logo attachment for {} team.'.format(location))

    scene_atch = None
    try:
        scene_atch = pm.PyNode('{0}_LOCATOR'.format(location))
    except:
        pm.warning('Build Scene  ERROR Could not find scene attachment for {} team.'.format(location))

    if (logo_atch) and (scene_atch):
        attach(scene_atch, logo_atch)
    return


def attachTeamToSign(location):
    ''' Attaches a team logo to its corresponding sign.  Location refers to home/away. '''
    location = location.upper()

    sign_namespace = '{0}SIGN'.format(location)
    logo_namespace = '{0}LOGO'.format(location)

    sign_atch_board = None
    logo_atch_board = None

    # Get basic attachment points
    try:
        sign_atch_board  = pm.PyNode('{0}:ATTACH_01'.format(sign_namespace))
        sign_atch_bldg   = pm.PyNode('{0}:ATTACH_05'.format(sign_namespace))
        sign_atch_mascot = pm.PyNode('{0}:ATTACH_06'.format(sign_namespace))

        logo_atch_board  = pm.PyNode('{0}:ATTACH_01'.format(logo_namespace))

    except:
        pm.warning('Build Scene  ERROR Critical attachment points not found for {0} team.'.format(location))
    
    # Get optional attachment points.  These do not exist in every element.
    try:
        logo_atch_bldg   = pm.PyNode('{0}:ATTACH_05'.format(logo_namespace))
    except: logo_atch_bldg = None
    try:
        logo_atch_mascot = pm.PyNode('{0}:ATTACH_06'.format(logo_namespace))
    except: logo_atch_mascot = None

    if (sign_atch_board) and (logo_atch_board):
        attach(sign_atch_board, logo_atch_board)

    if (logo_atch_bldg):
        attach(sign_atch_bldg, logo_atch_bldg)
    if (logo_atch_mascot):
        attach(sign_atch_mascot, logo_atch_mascot)    
    return


def attachSignToScene(location):
    ''' Attaches a sign to its corresponding locator in the scene.  Location refers to home/away '''
    location = location.upper()

    sign_namespace = '{0}SIGN'.format(location)

    scene_loc = None
    sign_loc = None

    # Check for attachment locators
    try:
        scene_loc = pm.PyNode('{0}_LOCATOR'.format(location))
    except: 
        pm.warning('Build Scene  ERROR Missing sign attachment locator for {0} team.'.format(location))
        return

    try:
        sign_loc = pm.PyNode('{0}SIGN:MAIN_POS'.format(location))
    except:
        pm.warning('Build Scene  ERROR Could not find sign master control curve for {0} team.'.format(location))
        return

    if (scene_loc) and (sign_loc):
        attach(scene_loc, sign_loc)

    return


def attachRegion(location):
    ''' Attaches a region object to its corresponding locator in the scene.  Location refers to
        home/away '''
    location = location.upper()

    region_namespace = '{0}REGION'.format(location)

    scene_loc = None
    region_loc = None

    try:
        scene_loc = pm.PyNode('REGION_LOCATOR')
    except:
        pm.warning('Build Scene  ERROR Missing scene attachment locator for region.')
    
    try:
        region_loc = pm.PyNode('{0}REGION:MAIN_POS'.format(location))
    except:
        pm.warning('Build Scene  ERROR Missing region attchment locator.')

    if (scene_loc) and (region_loc):
        attach(scene_loc, region_loc)

    return


def attachLightRig(location):
    ''' Attaches a light rig to its corresponding home/away locator in the scene.'''
    location = location.upper()

    lgtrig_namespace = '{0}_ENV_LGT'.format(location)

    scene_loc = None
    lgtrig_loc = None

    try:
        scene_loc = pm.PyNode('{}_LOCATOR'.format(location))
    except:
        pm.warning('Build Scene  ERROR Missing scene attachment locator for {0} team'.format(location))

    try:
        lgtrig_loc = pm.PyNode('{}_ENV_LGT:MAIN_POS'.format(location))
    except:
        pm.warning('Build Scene  ERROR Missing attachment locator for light rig for {0} team'.format(location))

    if (scene_loc) and (lgtrig_loc):
        attach(scene_loc, lgtrig_loc)

    return


def attachLayout(project):
    ''' Attaches a layout to its corresponding locator in the scene. 
        NOTE:  THIS ALSO INCLUDES THE LAYOUT LIGHT RIG FOR CONVENIENCE  '''
    
    scene_loc = None
    layout_loc = None
    lgtrig_loc = None

    try:
        scene_loc = pm.PyNode('LAYOUT_LOCATOR')
    except:
        pm.warning('Build Scene  ERROR Missing scene attachment locator for layout.')

    try:
        layout_loc = pm.PyNode('{}_LAYOUT|RIG|MAIN_POS'.format(project))
        lgtrig_loc = pm.PyNode('LAYOUT_ENV_LGT:MAIN_POS')
    except:
        pm.warning('Build Scene  ERROR Missing layout attachment locator or layout light rig locator.')

    if (scene_loc) and (layout_loc) and (lgtrig_loc):
        attach(scene_loc, layout_loc)
        attach(scene_loc, lgtrig_loc)

    return


def attach(parent, child):
    ''' Combines parent and scale constraining into one command. '''
    pc = pm.parentConstraint(parent, child, mo=False)
    sc = pm.scaleConstraint(parent, child, mo=False)
    return (pc,sc)


##############################################################################
### MAIN PROCEDURES ##########################################################
##############################################################################

def loadAssetsStadium(tricode, location, diagnostic=False, clean=True):
    # Get team info from database
    """ Given a specific location (home/away), this function attempts to reference
        in a selected team's assets and attach them to respected 01, 05 and 06
        attachment points."""
    try:
        team = Team(tricode)
    except: 
        pm.warning('Build Scene  ERROR Could not find team in database.')
        return

    # Generate string for the name of the school's sign
    sign = 'SIGN_{0}'.format(team.sign.upper())
    # Generate string for the school's matte painting ID
    mp_id = str(team.matteNum).zfill(2)

    
    ''' LK SPECIFIC SECTION '''
    # The full path of this scene
    this_scene = pm.sceneName()
    # Split into tokens
    scene_token = this_scene.split('/')
    # 4th from the right is the project name
    this_project = scene_token[len(scene_token)-1].replace('_SKELETON.mb', '')
    ''' END LK '''


    # Create paths for signs / team logo / region / layout scenes
    sign_path = os.path.join(cfb.MAIN_ASSET_DIR, sign, (sign+'.mb'))
    logo_path = os.path.join(cfb.TEAMS_ASSET_DIR, team.tricode, (team.tricode+'.mb'))
    lgtrig_path = os.path.join(cfb.MAIN_ASSET_DIR, 'LIGHTING_BASE', 'LIGHTING_BASE.mb')
    
    if (diagnostic):
        print '\n'
        print '{} Team:   {}'.format(location, team.tricode)
        print 'Project:     {}'.format(this_project)
        print '{} Sign:   {}'.format(location, sign_path)
        print '{} Logo:   {}'.format(location, logo_path)
        print 'Light Rig:   {}'.format(lgtrig_path)


    # Check for missing files and print warnings
    if not os.path.exists(sign_path):
        pm.warning('Build Scene  WARNING could not find {0}'.format(sign_path))
        sign_path = None
    if not os.path.exists(logo_path):
        pm.warning('Build Scene  WARNING could not find {0}'.format(logo_path))
        logo_path = None
    if not os.path.exists(lgtrig_path):
        pm.warning('Build Scene  WARNING could not find {0}'.format(lgtrig_path))
        lgtrig_path = None

    if (diagnostic):
        return

    # Generate namespaces
    sign_nspc = '{0}SIGN'.format(location)
    logo_nspc = '{0}LOGO'.format(location)

    # Check for existing references
    sign_ref = None
    logo_ref = None

    # Get those reference nodess
    for ref in pm.listReferences():
        if ref.namespace == sign_nspc:
            sign_ref = ref

        elif ref.namespace == logo_nspc:
            logo_ref = ref

    # If there are references missing, force a clean run for simplicity's sake (i implore you)
    if (sign_ref) or (logo_ref) == None and clean == False:
        pm.warning('Build Scene  Existing reference not found.  Forcing clean reference.')
        clean = True

    # If the user has asked to do a clean reference of the asset, including attachment
    if (clean):
        # If there's already references in those namespaces, just delete them
        if (logo_ref): logo_ref.remove()
        if (sign_ref): sign_ref.remove()
        # Reference in the asset to the namespace
        if sign_path: asset.reference(sign_path, sign_nspc)
        if logo_path: asset.reference(logo_path, logo_nspc)

        # Attach them to their parent locators
        attachTeamToSign(location)
        attachSignToScene(location)

    # (If) there are already references in the namespaces, and the user is requesting
    # to replace the reference and maintain reference edits (dirty mode)
    elif not (clean):
        # If the right sign is already loaded, pass
        if (sign+'.mb') in sign_ref.path:
            pass
        # Or else replace the sign reference
        else:
            sign_ref.replaceWith(sign_path)
        # Same thing with school logos this time
        if (team.tricode+'.mb') in logo_ref.path:
            pass
        else:
            logo_ref.replaceWith(logo_path)

    # Cleanup foster parents
    try:
        sign_re = re.compile('{0}RNfosterParent.'.format(sign_nspc))
        logo_re = re.compile('{0}RNfosterParent.'.format(logo_nspc))

        pm.delete(pm.ls(regex=sign_re))
        pm.delete(pm.ls(regex=logo_re))
    except:
        pass


def loadAssetsLite(tricode, location, diagnostic=True):
    ''' Load the selected team logo (only) into the specificed 'location' (home/away)
        as a namespace.
        LITE version attaches only the logo to a locator called HOME_LOCATOR.'''

    try:
        team = Team(tricode)
    except:
        pm.warning('Build Scene  ERROR Could not find team in database.')
        return

    # Generate target logo path and namespace
    logo_path = os.path.join(cfb.TEAMS_ASSET_DIR, team.tricode, (team.tricode+'.mb'))
    if not os.path.exists(logo_path):
        pm.warning('Build Scene  WARNING could not find {0}'.format(logo_path))
        return
    logo_nspc = '{}LOGO'.format(location)

    # Get existing reference nodes and kill them
    logo_ref = None
    for ref in pm.listReferences():
        if ref.namespace == logo_nspc:
            logo_ref = ref

    if (logo_ref): logo_ref.remove()

    # Reference the logo
    try:
        asset.reference(logo_path, logo_nspc)
    except:
        pm.warning('Build Scene  ERROR Could not reference {} logo.'.format(tricode))

    # Attach the logo
    try:
        attachTeamLite(location)
    except:
        pm.warning('Build Scene  ERROR Could not attach {} logo.'.format(tricode))       

    foster_re = re.compile('.RNfosterParent.')
    pm.delete(pm.ls(regex=foster_re))


def loadTeamsStadium(home_team, away_team=None, diagnostic=False, clean=True, *a):
    loadAssetsStadium(home_team, 'HOME', diagnostic, clean)
    if away_team:
        loadAssetsStadium(away_team, 'AWAY', diagnostic, clean)
    return


def loadTeamsLite(home_team, away_team=None, *a):
    ''' A lite version of loadTeams that skips signs and major authoring steps,
        only loading a team primary logo and attaching it to a scene locator.'''
    loadAssetsLite(home_team, 'HOME')
    if away_team:
        loadAssetsLite(away_team, 'AWAY')
    return

