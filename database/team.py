import yaml

from pipeline import cfb

## TEAM DATABASE OBJECT
class Team(object):
    def __init__(self, team_tricode):
        yaml_stream = open(cfb.TEAM_DATABASE)
        db = yaml.load_all(yaml_stream)
        found = 0
        
        # Converts matte painting index to its full name
        matte_conv = {
            1: 'MP01-pacNW',
            2: 'MP02-noCal',
            3: 'MP03-soCal',
            4: 'MP04-soWest',
            5: 'MP05-rockies',
            6: 'MP06-texas',
            7: 'MP07-okla',
            8: 'MP08-gtLakes',
            9: 'MP09-centPlains',
           10: 'MP10-midWest',
           11: 'MP11-soEast',
           12: 'MP12-deepSouth',
           13: 'MP13-appalach',
           14: 'MP14-centEast',
           15: 'MP15-noEast',
           16: 'MP16-soFla'
        }

        # Parse the db to find the team by tricode or name 
        for team in db:
            if (team['tricode'] == team_tricode) or (team['team'] == team_tricode):
                self.db = team
                found = 1
                break
        
        if not found:
            print 'Team not found in database!'

        else:    
            # Team info
            self.name     = team['team']
            self.nickname = team['mascot']
            self.safename = team['os_safe']
            self.tricode  = team['tricode']
            
            # Team categories
            self.conf     = self.db['conference']
            self.tier     = self.db['tier']

            # Team internal information
            self.sign     = team['sign']
            self.matte    = matte_conv[team['matte']]
            self.sky      = team['sky']
            self.acc      = (self.db['five'], self.db['six'])
            self.switch   = False
            
            # Team colors
            self.primary  = (self.db['primary'][0], 
                             self.db['primary'][1], 
                             self.db['primary'][2]
                             )
            self.secondary = (self.db['secondary'][0], 
                              self.db['secondary'][1], 
                              self.db['secondary'][2]
                              )
        
        yaml_stream.close()
    
    def __repr__(self):
        return '{0}\n{1} {2}'.format(self.tricode, self.name, self.nickname)

def getAllTeams( database, asNames=False, asDict=False ):
    with open(database) as yaml_stream:
        stream = yaml.load_all(yaml_stream)
    
    if asNames:
        return [t['team'] for t in stream]
    elif asDict:
        return [t for t in stream]
