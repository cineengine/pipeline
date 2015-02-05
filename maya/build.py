import pymel.core as pm

# CFB modules

# Internal modules
from pipeline.db import Team
import pipeline.vray.renderElements as renderElements
import pipeline.vray.utils as utils
import pipeline.vray.mattes as mattes
import cg.maya.rendering as rendering
"""

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

    # REFERENCE FACTORY ELEMENTS
    # reference light rig
    pm.createReference(cfb.FACTORY_LIGHT_RIG, namespace='FACTORY')
    # build framebuffers
    passes(cfb.FRAMEBUFFERS['beauty'])
    passes(cfb.FRAMEBUFFERS['utility'])
    # get sorting template from DB
    factory_sorting = SortDict('Factory')
    # sort scene
    sceneFromDb(factory_sorting)
    
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

        else: pass
        


def attachTeamToSign(sign_name, team_name, do_attach=True):
    def _attach( obj, anchor ):
        pc = pm.parentConstraint( anchor, obj, mo=False )
        return pc

    team = Team(team_name)
    #print team.name
    
    ## Getting all the relevant attachment objects and maya nodes
    try:
        print sign_name
        sign = pm.PyNode(sign_name + ':' + sign_name)
        print sign
        
        #sign_primary   = pm.PyNode(sign_name + ':TEAM_PRIMARY.colorEntryList[0].color')
        #print sign_primary
        #sign_secondary = pm.PyNode(sign_name + ':TEAM_SECONDARY.colorEntryList[0].color')
        #print sign_secondary
        #sign_tex_two   = pm.PyNode(sign_name + ':TEAM_02.fileTextureName')
        #print sign_tex_two
        #sign_tex_three = pm.PyNode(sign_name + ':TEAM_03.fileTextureName')
        #print sign_tex_three
        #sign_tex_four  = pm.PyNode(sign_name + ':TEAM_04.fileTextureName')
        #print sign_tex_four

        if do_attach:
            sign_attach_one = pm.PyNode(sign_name + ":" + 'ATTACH_01')
            print sign_attach_one
            team_attach_one = pm.PyNode(team_obj.tricode + ":" + 'ATTACH_01')
            print team_attach_one
            # Physically attach logo to panel_01
            _attach( team_attach_one, sign_attach_one )

            warn = 'Could not find 5 or 6 asset for ' + str(team.name)
            if team.acc[0]:
                try:
                    sign_attach_five = pm.PyNode(sign_name + ":" + 'ATTACH_05')
                    team_attach_five = pm.PyNode(team_obj.tricode + ":" + 'ATTACH_05')
                    # Physically attach #5 element to #5 attach spot
                    _attach( team_attach_five, sign_attach_five )
                except:
                    pm.warning(warn)
                
            # #6 element
            if team.acc[1]:
                try:
                    sign_attach_six = pm.PyNode(sign_name + ":" + 'ATTACH_06')
                    team_attach_six = pm.PyNode(team_obj.tricode + ":" + 'ATTACH_06')            
                    # Physically attach #6 element to #6 attach spot
                    _attach( team_attach_six, sign_attach_six )
                except:
                    pm.warning(warn)

    except:
        pm.warning('Error finding team or sign attachment object.')
        return False

    ## Colors & Textures
    #sign_primary.set( rendering.convertColor(team.primary) )
    #sign_secondary.set( rendering.convertColor(team.secondary) )

    #tex_location = cfb.TEAMS_ASSET_DIR + "/" + team.tricode + "/includes/" + team.tricode + "_"

    #sign_tex_two.set(tex_location + "02.png")
    #sign_tex_three.set(tex_location + "03.png")
    #sign_tex_four.set(tex_location + "04.png")

    return True

def attachTeamToSignUI(*a):
    sel = pm.ls(sl=True)[0]
    print sel
    name = str(sel).split(':')[1]

    win = pm.window('enterTeam',
                    tlb=True, rtf=True, s=False,
                    title = 'EnterTeam Name'
                    )
    lay = pm.verticalLayout(width = 250, p=win)
    text = pm.textFieldGrp( label='Team Name : ', p=lay, cw2=(70,130))
    but = pm.button(label='Attach', c=lambda *args: attachTeamToSign(name, pm.textFieldGrp(text, q=True, tx=True), do_attach=False), p=lay)
    lay.redistribute()
    win.show()

"""


# Useful for arbitrary keyword argument reference
#def attachElements(typ, **kwargs):
#    ''' Attaches elements from a single subordinate asset to a framework asset.
#        e.g. Team elements to a sign
#        Usage example:  attachElements('sign', sign='SIGN_A', team='WIS')'''
#    
#    def _attach( obj, anchor ):
#        pc = pm.parentConstraint( anchor, obj, mo=False )
#        return pc
#    
#    # Attaching team assets to a sign
#    if typ == 'sign':
#        # If typ is 'sign', optional keywords must be a 'sign' asset and a 'team' tricode
#        if kwargs is not None:
#            # Get the sign and team
#            for asset, name in kwargs.iteritems():
#                if asset == 'sign':
#                    sign_name = name
#                elif asset == 'team':
#                    team_obj = db.Team(name)
#                
#            # Attach team #1 element to sign #1 attachment point    
#            sign_attach_one = pm.PyNode(sign_name + ":" + 'ATTACH_01')
#            team_attach_one = pm.PyNode(team_obj.tricode + ":" + 'ATTACH_01')
#            _attach( team_attach_one, sign_attach_one )
#            
#            # #5 element
#            warn = 'Could not find 5 or 6 asset for ' + str(team_obj.tricode)
#            if team_obj.acc[0]:
#                try:
#                    sign_attach_five = pm.PyNode(sign_name + ":" + 'ATTACH_05')
#                    team_attach_five = pm.PyNode(team_obj.tricode + ":" + 'ATTACH_05')
#                    _attach( team_attach_five, sign_attach_five )
#                except:
#                    pm.warning(warn)
#                
#            # #6 element
#            if team_obj.acc[1]:
#                try:
#                    sign_attach_six = pm.PyNode(sign_name + ":" + 'ATTACH_06')
#                    team_attach_six = pm.PyNode(team_obj.tricode + ":" + 'ATTACH_06')            
#                    _attach( team_attach_six, sign_attach_six )
#                except:
#                    pm.warning(warn)
#                    
#        # There must be optional keywords or else there's nothing to do
#        else:
#            pm.warning('No asset keywords passed to attachElements()')
#            return False
#    #elif typ == 'template':
#    #elif typ == 'logo':
        

"""
def mayaScene( home_team, away_team, package, week ):

    home_team = Team(home_team)
    away_team = Team(away_team)
    package = Package(package)

    ## Package refers to "gameday", "primetime", etc

    ## Package.scenelist is a list of dictionaries
    ## each "scene" dictionary key/value pair corresponds to a bit of information about
    ## an individual scene that makes up a package.  Assets to reference, frame in/out,
    ## render layers, render elements, and a sorting dictionary.

    for scene in package.scenelist:

        ## scene[values] are just lists of strings which key to dicionaries 
        ## in their respective classes / function calls

        pm.newScene
        pm.saveSceneAs(path\week\scene)

        # home/away_assets will include offset information somehow
        # package_assets will include cameras, light rigs, etc
        __referenceAssets( home_team, scene[home_assets] )
        __referenceAssets( away_team, scene[away_assets] )
        __referenceAssets( package, scene[package_assets] )

        # the easy part
        __setRenderGlobals( scene[anim_data] )
        __createRenderLayers( scene[layers] )
        __createRenderElements( scene[render_elements] )

        # the annoying part
        __sortAssets( scene[sort_dict] )

        pm.saveScene
        pm.closeScene


def nukeScene( home_team, away_team, package, week ):
"""