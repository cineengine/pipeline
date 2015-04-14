import yaml

from pipeline import cfb

## TEAM DATABASE OBJECT
class Team(object):
    def __init__(self, team_tricode):
        yaml_stream = open(cfb.TEAM_DATABASE)
        db = yaml.load_all(yaml_stream)
        found = 0
        # Parse the db to find the team by tricode or name 
        for team in db:
            if (team['tricode'] == team_tricode) or (team['team'] == team_tricode):
                self.db = team
                found = 1
                break
        
        if not found:
            print 'Team not found in database!'

        else:    
            # Team name
            self.name = self.db['team']
            self.nickname = self.db['mascot']
            self.safename = self.db['os_safe']
            self.tricode = self.db['tricode']
            self.matte = self.db['matte']
            self.sky = self.db['sky']
            self.sign = self.db['sign']
            
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
    
    def __repr__(self):
        return self.name + " " + self.nickname + " (" + self.tricode + ")\n TIER " + str(self.tier) + " :: Five / Six: " + str(self.acc) + " :: "


def getAllTeams( database, asNames=False, asDict=False ):
    with open(database) as yaml_stream:
        stream = yaml.load_all(yaml_stream)
    
    if asNames:
        return [t['team'] for t in stream]
    elif asDict:
        return [t for t in stream]

