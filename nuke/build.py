from pipeline import cfb
import pipeline.database.team as t

import nuke
import threading, thread

import time
from os import makedirs
from os.path import exists
from os.path import split

# Modify gvars for nuke-friendliness
TEAMS_ASSET_DIR = cfb.TEAMS_ASSET_DIR.replace('\\','/')

BASE_OUTPUT_DIR = 'F:/04_CG_Projects/Test'

# Node names from Nuke
MASTER_CTRL = "MASTER_CTRL"
MASTER_WRITE = "MASTER_WRITE"

logo_read_nodes = ['READ_HOME_SUNSET',
                   'READ_HOME_NIGHT',
                   'READ_HOME_MATTE',
                   'READ_HOME_UTIL',
                   'READ_AWAY_SUNSET',
                   'READ_AWAY_NIGHT',
                   'READ_AWAY_MATTE',
                   'READ_AWAY_UTIL'
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
        logoReadNode = nuke.toNode('READ_{}_LOGO'.format(location.upper()))
        logoReadNode.knob('file').setValue(team2DAssetString(team.tricode, 1))
    except: pass


def selectTeamPodTwo(location, team):
    try:
        podTwoReadNode = nuke.toNode('READ_{}_POD_TWO'.format(location.upper()))
        podTwoReadNode.knob('file').setValue(team2DAssetString(team.tricode, 2))
    except: pass


def selectTeamPodThree(location, team):
    try:
        podThreeReadNode = nuke.toNode('READ_{}_POD_THREE'.format(location.upper()))
        podThreeReadNode.knob('file').setValue(team2DAssetString(team.tricode, 3))
    except: pass


def selectTeamBanner(location, team):
    try:
        bannerReadNode = nuke.toNode('READ_{}_BANNER'.format(location.upper()))
        bannerReadNode.knob('file').setValue(team2DAssetString(team.tricode, 4))
    except: pass


def selectLogoRender(location, team):
    # figure out which project this scene is in
    proj_name = getProject()
    logo_path = cfb.ANIMATION_PROJECT_DIR + proj_name + "/render_3d/LOGOS/" + team.tricode + "/"
    
    for r in logo_read_nodes:
        pass_path = ""
        try:
            # get the read node
            rn = nuke.toNode(r)
            # figure out the file names on this node
            pass_path = rn.knob('file').getValue().split('/')
            if len(pass_path) == 1:
                pass_path = rn.knob('file').getValue().split('/')
            # getting layerName/layerName.#.ext
            pass_path = pass_path[len(pass_path)-2] + "/" + pass_path[len(pass_path)-1]
            # replace the path prefix with the correct project/team logo version
            rn.knob('file').setValue(logo_path + pass_path)
            #print logo_path + pass_path
        except:
            nuke.warning('Error finding replacement for: ' + r)



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
    # INCLUDE FOLDER SANITY CHECK AND APPEND REST OF DIRECTORY

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
