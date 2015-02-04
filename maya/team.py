import yaml
#import cfb

class Team(object):
    def __init__(self, school):
        yaml_stream = open(cfb.TEAM_DATABASE)
        stream = yaml.load_all(yaml_stream)

        # Parse the db to find the team
        for t in stream:
            if t['team'] == school:
                self.db = t
                break
        
        # Team name
        self.name = self.db['team']
        self.nickname = self.db['mascot']
        self.safename = self.db['os_safe']
        self.tricode = self.db['tricode']
        
        # Team categories
        self.conf = self.db['conference']
        self.tier = self.db['tier']
        
        # Team accoutrement used
        self.acc = (self.db['five'], self.db['six'])
        
        # Team colors
        self.primary = (self.db['primary'][0], 
                        self.db['primary'][1], 
                        self.db['primary'][2]
                        )
        self.secondary = (self.db['secondary'][0], 
                          self.db['secondary'][1], 
                          self.db['secondary'][2]
                          )
        
        yaml_stream.close()

#def buildFolders( home_team, away_team, week ):

"""
def buildMaya( home_team, away_team, package, week ):

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


def buildNuke( home_team, away_team, package, week ):
"""

def getAllTeams( asNames=False, asDict=False ):
    yaml_stream = open(team_yaml_db)
    stream = yaml.load_all(yaml_stream)
    
    if asNames:
        return [t['team'] for t in stream]
    elif asDict:
        return [t for t in stream]




