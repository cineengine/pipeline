from pipeline import cfb
import pipeline.database.team as t
reload(t)

import nuke
import threading, thread

import time
from os import mkdir
from os.path import exists
from os.path import split

# Modify gvars for nuke-friendliness
TEAMS_ASSET_DIR = cfb.TEAMS_ASSET_DIR.replace('\\','/')

# Node names from Nuke
MASTER_CTRL = "MASTER_CTRL"

READ_LOGO = "READ_TEAM_LOGO"
READ_BANNER = "READ_TEAM_BANNER"
READ_PODTWO = "READ_POD_TWO"
READ_PODTHREE = "READ_POD_THREE"

READ_AWAY_LOGO = "READ_AWAY_LOGO"
READ_AWAY_BANNER = "READ_AWAY_BANNER"
READ_AWAY_PODTWO = "READ_AWAY_POD_TWO"
READ_AWAY_PODTHREE = "READ_AWAY_POD_THREE"

logo_read_nodes = ['READ_TEAM_SUNSET',
                   'READ_TEAM_NIGHT',
                   'READ_TEAM_MATTE',
                   'READ_TEAM_UTIL',
                   'READ_AWAY_SUNSET',
                   'READ_AWAY_NIGHT',
                   'READ_AWAY_MATTE',
                   'READ_AWAY_UTIL'
                   ]


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


def loadTeam(textTrans=False, renders=True, matchup=False):
    ctrlNode = nuke.toNode(MASTER_CTRL)
    #k = nuke.thisKnob()
    #if k.name() == "teamTricode":
    #    tricode = k.getValue()
    tricode = ctrlNode.knob('teamTricode').getValue()

    selectColors(tricode)
    selectRegions(tricode)
    selectSkies(tricode)
    selectSigns(tricode)
    selectTeamLogo(tricode)
    selectTeamBanner(tricode)
    selectTeamPodTwo(tricode)
    selectTeamPodThree(tricode)

    if matchup:
        away_tricode = ctrlNode.knob('awayTeamTricode').getValue()
        selectColors(away_tricode, away=True)
        selectRegions(away_tricode, away=True)
        selectSkies(away_tricode, away=True)
        selectSigns(away_tricode, away=True)
        selectTeamLogo(away_tricode, away=True)
        selectTeamBanner(away_tricode, away=True)
        selectTeamPodTwo(away_tricode, away=True)
        selectTeamPodThree(away_tricode, away=True)
    

def writeThread(write_node, start_frame, end_frame):
    nuke.executeInMainThread(nuke.execute, args=(write_node, start_frame, end_frame, 1), kwargs={'continueOnError':False})


def initTeamToRender(tricode, location):
    m_ctrl = nuke.toNode('MASTER_CTRL')
    m_write = nuke.toNode('MAIN_WRITE')

    team = t.Team(tricode)

    m_write.knob('{}_team'.format(location)).setValue(tricode)
    m_write.knob('{}_sign'.format(location)).setValue(team.sign)
    m_write.knob('{}_region'.format(location)).setValue(int(team.matteNum))
    if location == 'home':
        m_write.knob('sky').setValue(int(team.skyNum))


def preRender():
    m_ctrl = nuke.toNode('MASTER_CTRL')
    m_write = nuke.toNode('MAIN_WRITE')

    matchup = bool(m_write.knob('is_matchup').getValue())
    
    team_list = m_write.knob('team_list').getValue().split(',')

    print team_list[0]

    initTeamToRender(team_list[0], 'home')
    
    # make output folders

def postRender():
    m_write = nuke.toNode('MAIN_WRITE')

    team_list = m_write.knob('team_list').getValue().split(',')
    del team_list[0]
    m_write.knob('team_list').setValue(','.join(team_list))
    
    if len(team_list) == 0:
        return

    else:
        render_thread = threading.Thread(name='writeThread', target=writeThread, args=(m_write, 1, 1))
        render_thread.setDaemon(False)
        render_thread.start()

        while render_thread.isAlive():
            time.sleep(0.1)


def preFrame():
    pass


def postFrame():
    pass


def selectColors(tricode, away=False):    
    team = t.Team(tricode)
    ctrlNode = nuke.toNode(MASTER_CTRL)
    if not away:
        try:
            ctrlNode.knob('primaryColor').setValue(convertColor( team.primary, toFloat=True ))
            ctrlNode.knob('secondaryColor').setValue(convertColor( team.secondary, toFloat=True ))
        except: pass
    elif away:
        try:
            ctrlNode.knob('awayPrimaryColor').setValue(convertColor( team.primary, toFloat=True ))
            ctrlNode.knob('awaySecondaryColor').setValue(convertColor( team.secondary, toFloat=True ))
        except: pass


def selectRegions(tricode, away=False):    
    team = t.Team(tricode)
    ctrlNode = nuke.toNode(MASTER_CTRL)
    if not away:
        try:
            ctrlNode.knob('Region').setValue( team.matte )
            ctrlNode.knob('RegionNum').setValue( team.matteNum )
        except: pass
    elif away:
        try:
            ctrlNode.knob('AwayRegion').setValue( team.matte )
            ctrlNode.knob('AwayRegionNum').setValue( team.matteNum )
        except: pass


def selectSkies(tricode, away=False):    
    team = t.Team(tricode)
    ctrlNode = nuke.toNode(MASTER_CTRL)
    if not away:
        try:
            ctrlNode.knob('Sky').setValue( team.sky )
            ctrlNode.knob('SkyNum').setValue( team.skyNum )
        except: pass
    elif away:
        try:
            ctrlNode.knob('AwaySky').setValue( team.sky )
            ctrlNode.knob('AwaySkyNum').setValue( team.skyNum )
        except: pass


def selectSigns(tricode, away=False):    
    team = t.Team(tricode)
    ctrlNode = nuke.toNode(MASTER_CTRL)
    if not away:
        try:
            ctrlNode.knob('Sign').setValue( team.sign )
            ctrlNode.knob('SignNum').setValue( team.signNum )
        except: pass
    elif away:
        try:
            ctrlNode.knob('AwaySign').setValue( team.sign )
            ctrlNode.knob('AwaySignNum').setValue( team.signNum )
        except: pass


def selectTeamLogo(tricode, away=False):
    if not away:
        try:
            logoReadNode = nuke.toNode(READ_LOGO)
            logoReadNode.knob('file').setValue(TEAMS_ASSET_DIR + tricode + "/includes/" + tricode + "_01.PNG")
        except: pass
    elif away:
        try:
            logoReadNode = nuke.toNode(READ_AWAY_LOGO)
            logoReadNode.knob('file').setValue(TEAMS_ASSET_DIR + tricode + "/includes/" + tricode + "_01.PNG")
        except: pass        


def selectTeamBanner(tricode, away=False):
    if not away:
        try:
            bannerReadNode = nuke.toNode(READ_BANNER)
            bannerReadNode.knob('file').setValue(TEAMS_ASSET_DIR + tricode + "/includes/" + tricode + "_04.PNG")
        except: pass
    elif away:
        try:
            bannerReadNode = nuke.toNode(READ_AWAY_BANNER)
            bannerReadNode.knob('file').setValue(TEAMS_ASSET_DIR + tricode + "/includes/" + tricode + "_04.PNG")
        except: pass


def selectTeamPodTwo(tricode, away=False):
    if not away:
        try:
            podTwoReadNode = nuke.toNode(READ_PODTWO)
            podTwoReadNode.knob('file').setValue(TEAMS_ASSET_DIR + tricode + "/includes/" + tricode + "_02.PNG")
        except: pass
    elif away:
        try:
            podTwoReadNode = nuke.toNode(READ_AWAY_PODTWO)
            podTwoReadNode.knob('file').setValue(TEAMS_ASSET_DIR + tricode + "/includes/" + tricode + "_02.PNG")
        except: pass


def selectTeamPodThree(tricode, away=False):
    if not away:
        try:
            podThreeReadNode = nuke.toNode(READ_PODTHREE)
            podThreeReadNode.knob('file').setValue(TEAMS_ASSET_DIR + tricode + "/includes/" + tricode + "_03.PNG")
        except: pass
    elif away:
        try:
            podThreeReadNode = nuke.toNode(READ_AWAY_PODTHREE)
            podThreeReadNode.knob('file').setValue(TEAMS_ASSET_DIR + tricode + "/includes/" + tricode + "_03.PNG")
        except: pass


def selectLogoRender(tricode):
    # figure out which project this scene is in
    proj_name = getProject()
    logo_path = cfb.ANIMATION_PROJECT_DIR + proj_name + "/render_3d/LOGOS/" + tricode + "/"
    
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

