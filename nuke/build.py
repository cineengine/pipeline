# Built-in packages
import time
from os import makedirs
from os.path import exists
from os.path import split

# Nuke packages
import nuke
import threading, thread

# External packages
from pipeline import cfb
import pipeline.database.team as t


# Modify gvars for nuke-friendliness
TEAMS_ASSET_DIR = cfb.TEAMS_ASSET_DIR.replace('\\','/')

BASE_OUTPUT_DIR = 'F:/04_CG_Projects/Test'

# Node names from Nuke
MASTER_CTRL = "MASTER_CTRL"
MASTER_WRITE = "MASTER_WRITE"

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
## To-Do List  ##############################################################
#############################################################################

# Documentation
# Re-write selectLogoRender()

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


def selectLogoRender(home, away=None):
    package     = m_ctrl.knob('tod').getValue()
    matchup     = m_ctrl.knob('is_matchup').getValue()
    deliverable = m_ctrl.knob('deliverable').getValue()

    # Get a list of read nodes for this deliverable type
    logo_render_reads = {
        0.0: STUDIO_LOGO_READS,
        1.0: EVENT_LOGO_READS,
        2.0: EVENT_LOGO_READS,
        3.0: CITY_LOGO_READS,
        4.0: CITY_LOGO_READS 
        }[package]

    # Get base 3d render folder
    base_render_path = '{}/{}/render_3d'.format(BASE_OUTPUT_DIR, deliverable)
    # Base strings for sequence / folder names
    bty_render = 'bty{}Logo'
    util_render = 'util{}Logo'

    # Home Team render path generation
    bty_render_path = '{}/{}/{}.#.exr'.format(
        base_render_path, 
        home, 
        bty_render.format('home'),
        bty_render.format('home')
        )
    util_render_path = '{}/{}/{}.#.exr'.format(
        base_render_path, 
        home, 
        util_render.format('home'),
        util_render.format('home')
        )

    for home_read in logo_render_reads:
        home_read = nuke.toNode(home_read.format('home'.upper()))
        home_read.knob('file').setValue()

    # Get renders for the home team
    logo_path = cfb.ANIMATION_PROJECT_DIR + proj_name + "/render_3d/LOGOS/" + team.tricode + "/"




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
    return ('{0}_{1}/includes/{2}_0{3}.png'.format(TEAMS_ASSET_DIR, tricode, tricode, str(num)))



#############################################################################
## WEDGE RENDER FUNCTIONS ###################################################
#############################################################################


def setOutputPath(create_dirs=False):
    m_ctrl = nuke.toNode(MASTER_CTRL)
    m_write = nuke.toNode(MASTER_WRITE)
    
    package     = m_ctrl.knob('tod').getValue()
    matchup     = m_ctrl.knob('is_matchup').getValue()
    deliverable = m_ctrl.knob('deliverable').getValue()

    # Container list for all version tokens
    version_tokens = []

    base_dir = "{}/{}/render_2d/TEAMS".format(BASE_OUTPUT_DIR, deliverable)

    # Get show ID tag
    show_str = {
        0.0: '',
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
    version_tokens.append(away_team)

    version_str = '_'.join(version_tokens)
    version_str.rstrip('_')
    version_str.lstrip('_')

    version_dir = base_dir + '/' + version_str
    out_str = '{}/{}_{}.%04d.png'.format(version_dir, deliverable, version_str)  

    if (create_dirs):
        if not exists(version_dir):
            makedirs(version_dir)
    
    m_write.knob('file').setValue(out_str)
    return


def preRender():
    m_ctrl = nuke.toNode(MASTER_CTRL)

    matchup = bool(m_ctrl.knob('is_matchup').getValue())
    
    team_list = m_ctrl.knob('team_list').getValue().split(',')

    loadTeam('home', team_list[0], renders=False)
    if matchup: 
        loadTeam('away', team_list[0], renders=False)
    
    setOutputPath(create_dirs=True)


def postRender():
    m_ctrl = nuke.toNode(MASTER_CTRL)
    m_write = nuke.toNode(MASTER_WRITE)

    team_list = m_ctrl.knob('team_list').getValue().split(',')
    del team_list[0]
    m_ctrl.knob('team_list').setValue(','.join(team_list))
    
    if len(team_list) == 0:
        print 'stopping!'
        return

    else:
        print 'starting!'
        render_thread = threading.Thread(name='writeThread', target=writeThread, args=(m_write, 1, 1))
        render_thread.setDaemon(False)
        render_thread.start()

        while render_thread.isAlive():
            time.sleep(0.1)


def preFrame():
    pass


def postFrame():
    pass
