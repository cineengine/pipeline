# Built-in packages
import time
from os import makedirs
from os import mkdir
from os.path import exists
from os.path import split
from os.path import join

# Nuke packages
import nuke
import threading, thread

# External packages
from pipeline import cfb
from pipeline.nuke import submit
import pipeline.database.team as t
reload(t)
reload(submit)


# Modify gvars for nuke-friendliness
TEAMS_ASSET_DIR = cfb.TEAMS_ASSET_DIR.replace('\\','/')

BASE_OUTPUT_DIR = cfb.ANIMATION_PROJECT_DIR.replace('\\','/')

# Node names from Nuke
MASTER_CTRL = "MASTER_CTRL"
MASTER_WRITE = "MASTER_WRITE"

# Split matchup write nodes
SPLIT_WRITE_NODES = [
    "WRITE_HOME_FILL",
    "WRITE_AWAY_FILL",
    "WRITE_HOME_MATTE"
    ]

PRIMARY_LOGO_READ = 'READ_{}_LOGO'
SECONDARY_LOGO_READ = 'READ_{}_POD_TWO'
TERTIARY_LOGO_READ = 'READ_{}_POD_THREE'
BANNER_LOGO_READ = 'READ_{}_BANNER'

EVENT_LOGO_READS = [
    'READ_{}_SUNSET',
    'READ_{}_NIGHT',
    'READ_{}_UTIL'
    ]

STUDIO_LOGO_READS = [
    'READ_{}_NOON',
    'READ_{}_UTIL'
    ]

CITY_LOGO_READS = [
    'READ_{}_NIGHT',
    'READ_{}_UTIL'
    ]


#############################################################################
## LOAD TEAM FUNCTIONS ######################################################
#############################################################################

def loadTeam(location, tricode=None, renders=False):
    m_ctrl = nuke.toNode(MASTER_CTRL)

    if not (tricode):
        tricode = m_ctrl.knob('{}_team'.format(location)).getValue()
    elif (tricode):
        m_ctrl.knob('{}_team'.format(location)).setValue(tricode)

    team = t.Team(tricode)

    m_ctrl.knob('{}_sign'.format(location)).setValue(team.signNum)
    m_ctrl.knob('{}_region'.format(location)).setValue(int(team.matteNum))
    if location == 'home':
        m_ctrl.knob('sky').setValue(int(team.skyNum))

    selectColors(location, team)
    selectColorVariants(location, team)
    selectRegions(location, team)
    selectSkies(location, team)
    selectSigns(location, team)
    selectTeamLogo(location, team)
    selectTeamBanner(location, team)
    selectTeamPodTwo(location, team)
    selectTeamPodThree(location, team)
    if renders:
        selectLogoRender(location, team)


def selectColors(location, team):    
    primary = convertColor(team.primary, toFloat=True)
    secondary = convertColor(team.secondary, toFloat=True)

    m_ctrl = nuke.toNode(MASTER_CTRL)

    try:
        m_ctrl.knob('{}_primary'.format(location)).setValue(primary)
        m_ctrl.knob('{}_secondary'.format(location)).setValue(secondary)
    except: pass


def selectColorVariants(location, team):
    m_ctrl = nuke.toNode(MASTER_CTRL)

    try:
        m_ctrl.knob('{}_bboard_color'.format(location)).setValue(team.billboard)
        m_ctrl.knob('{}_neon_color'.format(location)).setValue(team.neon)
    except: pass


def selectRegions(location, team):    
    m_ctrl = nuke.toNode(MASTER_CTRL)
    try:
        m_ctrl.knob('{}_region'.format(location)).setValue( team.matteNum )
    except: pass


def selectSkies(location, team):    
    m_ctrl = nuke.toNode(MASTER_CTRL)
    try:
        m_ctrl.knob('sky').setValue( team.skyNum )
    except: pass


def selectSigns(location, team):    
    m_ctrl = nuke.toNode(MASTER_CTRL)
    try:
        m_ctrl.knob('{}_sign'.format(location)).setValue( team.signNum )
    except: pass


def selectTeamLogo(location, team):
    try:
        logoReadNode = nuke.toNode(PRIMARY_LOGO_READ.format(location.upper()))
        logoReadNode.knob('file').setValue(team2DAssetString(team.tricode, 1))
    except: pass


def selectTeamPodTwo(location, team):
    try:
        podTwoReadNode = nuke.toNode(SECONDARY_LOGO_READ.format(location.upper()))
        podTwoReadNode.knob('file').setValue(team2DAssetString(team.tricode, 2))
    except: pass


def selectTeamPodThree(location, team):
    try:
        podThreeReadNode = nuke.toNode(TERTIARY_LOGO_READ.format(location.upper()))
        podThreeReadNode.knob('file').setValue(team2DAssetString(team.tricode, 3))
    except: pass


def selectTeamBanner(location, team):
    try:
        bannerReadNode = nuke.toNode(BANNER_LOGO_READ.format(location.upper()))
        bannerReadNode.knob('file').setValue(team2DAssetString(team.tricode, 4))
    except: pass


def selectLogoRender(location, team):
    m_ctrl = nuke.toNode(MASTER_CTRL)

    package     = m_ctrl.knob('tod').getValue()

    logo_render_reads = {
        0.0: STUDIO_LOGO_READS,
        1.0: EVENT_LOGO_READS,
        2.0: EVENT_LOGO_READS,
        3.0: CITY_LOGO_READS,
        4.0: CITY_LOGO_READS 
        }[package]

    for rn in logo_render_reads:
        rn = rn.format(location.upper())
        rn = nuke.toNode(rn.format(location.upper()))
        render_path = rn.knob('file').getValue().split('/')
        render_path[-3] = team.tricode
        new_path = '/'.join(render_path)

        rn.knob('file').setValue(new_path)



#############################################################################
## HELPER FUNCTIONS #########################################################
#############################################################################

def convertColor( rgb_tuple, toFloat=True, toInt=False ):
    def __clamp(value):
        if value < 0: return 0
        if value > 255: return 255

    if toFloat:
        out_r = (1.0/255) * rgb_tuple[0]
        out_g = (1.0/255) * rgb_tuple[1]
        out_b = (1.0/255) * rgb_tuple[2]
        return (out_r, out_g, out_b)
    if toInt:
        out_r = __clamp(int(255 * rgb_tuple[0]))
        out_g = __clamp(int(255 * rgb_tuple[1]))
        out_b = __clamp(int(255 * rgb_tuple[2]))
        return (out_r, out_g, out_b)


def writeThread(write_node, start_frame, end_frame):
    nuke.executeInMainThread(nuke.execute, args=(write_node, start_frame, end_frame, 1), kwargs={'continueOnError':True})


def team2DAssetString(tricode, num):
    asset = '{0}{1}/includes/{2}_0{3}.png'.format(TEAMS_ASSET_DIR, tricode, tricode, str(num))
    print asset
    return asset


def setOutputPath(create_dirs=False, matchup=False, jumbo=False):
    m_ctrl = nuke.toNode(MASTER_CTRL)
    m_write = nuke.toNode(MASTER_WRITE)
    
    package     = m_ctrl.knob('tod').getValue()
    deliverable = m_ctrl.knob('deliverable').getValue()

    # Container list for all version tokens
    version_tokens = []

    base_dir = "{}/{}/render_2d/TEAMS".format(BASE_OUTPUT_DIR, deliverable)

    # Get show ID tag
    show_str = {
        0.0: 'STUDIO',
        1.0: 'CFB',
        2.0: 'PRIMETIME',
        3.0: 'SNF',
        4.0: 'PRIMETIME'
        }[package]
    version_tokens.append(show_str)

    # Get teams
    home_team   = m_ctrl.knob('home_team').getValue()
    if (matchup): 
        away_team = m_ctrl.knob('away_team').getValue()
    else: away_team = ''
    version_tokens.append(home_team)
    #version_tokens.append(away_team)

    version_str = '_'.join(version_tokens)
    version_str = version_str.lstrip('_')
    version_str = version_str.rstrip('_')

    if not (jumbo):
        version_dir = base_dir# + '/' + version_str
        out_str = '{}/{}_{}.%04d.png'.format(version_dir, deliverable, version_str)  

        if (create_dirs):
            if not exists(version_dir):
                makedirs(version_dir)
        
        m_write.knob('file').setValue(out_str)

        return

    elif (jumbo):
        home_dir = base_dir + '/' + version_str + '_HOME_FILL'
        home_str = '{}/{}_{}_HOME.%04d.png'.format(home_dir, deliverable, version_str)  
        matte_dir = base_dir + '/' + version_str + '_HOME_MATTE'
        matte_str = '{}/{}_{}_MATTE.%04d.png'.format(matte_dir, deliverable, version_str)  
        away_dir = base_dir + '/' + version_str + '_AWAY_FILL'
        away_str = '{}/{}_{}_AWAY.%04d.png'.format(away_dir, deliverable, version_str)  

        if (create_dirs):
            if not exists(home_dir):
                makedirs(home_dir)
            if not exists(matte_dir):
                makedirs(matte_dir)
            if not exists(away_dir):
                makedirs(away_dir)

        nuke.toNode('WRITE_HOME_FILL').knob('file').setValue(home_str)
        nuke.toNode('WRITE_HOME_MATTE').knob('file').setValue(matte_str)
        nuke.toNode('WRITE_AWAY_FILL').knob('file').setValue(away_str)

        return


#############################################################################
## GENERAL AUTOMATION #######################################################
#############################################################################

def createTeamScenes(team_list, range_, submit_to_farm=True, matchup=False):
    m_ctrl = nuke.toNode(MASTER_CTRL)
    deliverable = m_ctrl.knob('deliverable').getValue()
    out_dir = join(BASE_OUTPUT_DIR, deliverable, 'nuke', 'TEAMS')
    if not exists(out_dir): mkdir(out_dir)

    for team in team_list:
        scene_name = '{}_{}.nk'.format(deliverable, team)
        scene_path = join(out_dir, scene_name)
        loadTeam('home', team, renders=True)
        if matchup: 
            loadTeam('away', team, renders=True)
            setOutputPath(create_dirs=True, matchup=True)
        else:
            setOutputPath(create_dirs=True)

        nuke.scriptSaveAs(scene_path, 1)
        time.sleep(1)

        if submit_to_farm:
            
            if not matchup:
                submit.singleNode(
                    (deliverable + ' - ' + team),
                    scene_path,
                    range_,
                    '5000',
                    '16',
                    'MASTER_WRITE')
            
            elif matchup:
                submit.singleNode(
                    (deliverable + ' - ' + team + ' HOME'),
                    scene_path,
                    range_,
                    '5000',
                    '16',
                    'WRITE_HOME_FILL')
                submit.singleNode(
                    (deliverable + ' - ' + team + ' MATTE'),
                    scene_path,
                    range_,
                    '5000',
                    '16',
                    'WRITE_HOME_MATTE')
                submit.singleNode(
                    (deliverable + ' - ' + team + ' AWAY'),
                    scene_path,
                    range_,
                    '5000',
                    '16',
                    'WRITE_AWAY_FILL')                


#############################################################################
## WEDGE RENDER FUNCTIONS ###################################################
#############################################################################
def preRender(matchup=False, jumbo=False):
    m_ctrl = nuke.toNode(MASTER_CTRL)

    #matchup = bool(m_ctrl.knob('is_matchup').getValue())
    
    team_list = m_ctrl.knob('team_list').getValue().split(',')
    print team_list[0]

    loadTeam('home', team_list[0], renders=True)
    if matchup: 
        loadTeam('away', team_list[0], renders=True)
    
    setOutputPath(create_dirs=True, matchup=True, jumbo=False)


def postRender():
    m_ctrl = nuke.toNode(MASTER_CTRL)
    m_write = nuke.toNode(MASTER_WRITE)

    #start_frame = m_ctrl.knob('start_frame').getValue()
    #end_frame = m_ctrl.knob('end_frame').getValue()

    team_list = m_ctrl.knob('team_list').getValue().split(',')
    del team_list[0]
    m_ctrl.knob('team_list').setValue(','.join(team_list))
    
    if len(team_list) == 0:
        return

    else:
        render_thread = threading.Thread(name='', target=writeThread, args=(m_write, 60, 60))
        render_thread.setDaemon(False)
        render_thread.start()

        while render_thread.isAlive():
            time.sleep(0.1)


def preFrame():
    pass


def postFrame():
    pass
