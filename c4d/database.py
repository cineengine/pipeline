#    JSON Database operations for ESPN Animation projects pipeline
#    
#    Author:  Mark Rohrer
#    Contact: mark.rohrer@gmail.com
#    Version: 0.3
#    Date:    04/06/2016
#
#    
#
#    Features to be added: 

#
import c4d
import json
import os.path
#
from pipeline.c4d import error
reload(error)

DATABASE_PATH = "Y:\\Workspace\\SCRIPTS\\pipeline\\database"

# GETTERS ##########################################################################################
def getProduction(prod_):
    ''' Gets a production's global variables from the database. '''
    PRODUCTION_GLOBALS_DB = os.path.join(DATABASE_PATH, "productions_db.json")
    merged_prod = {}
    with open(PRODUCTION_GLOBALS_DB, 'r') as stream:
        full_db = json.load(stream)
        for k,v in full_db.iteritems():
            if (k == 'DEFAULT'):
                default_prod = full_db[k]
            elif (k == prod_):
                request_prod = full_db[k]
                request_prod['is_default'] = False
            else: request_prod = {'is_default': True}

    merged_prod = default_prod.copy()
    merged_prod.update(request_prod)
    return merged_prod

def getProductionDirty():
    ''' Infers the project based on where the current scene is located. '''
    scene_path = core.doc().GetDocumentPath()
    scene_path = scene_path.split('\\')
    prod_      = scene_path[3]

    try:
        prod   = PRODUCTIONS[proj_]
        return prod
    except KeyError:
        raise error.PipelineError(3)

def getAllProductions():
    ''' Gets a list of all available / valid productions from the database. '''
    PRODUCTION_GLOBALS_DB = os.path.join(DATABASE_PATH, "productions_db.json")
    productions = []
    with open(PRODUCTION_GLOBALS_DB, 'r') as stream:
        full_db = json.load(stream)
        for k,v in full_db.iteritems():
            if (k == 'DEFAULT'):
                continue
            else:
                productions.append(k)
    return sorted(productions)

def getAllProjects(prod_):
    ''' Gets all projects associated with a production.'''
    prod = getProduction(prod_)
    return [p for p in os.listdir(prod['project']) if os.path.isdir(os.path.join(prod['project'], p))]

def getTeamDatabase(prod_):
    ''' Gets the team database for a production. '''
    prod_db  = getProduction(prod_)
    if (prod_db['is_default'] == True):
        raise error.DatabaseError(1)

    team_db_ = prod_db['team_db']
    db_path  = os.path.join(DATABASE_PATH, '{0}.json'.format(team_db_))

    with open(db_path, 'r') as stream:
        full_db = json.load(stream)

    return full_db

def getTeam(prod_, tricode):
    ''' Gets a team from a production, based on tricode or full name.'''
    team_db = getTeamDatabase(prod_)
    for k,v in team_db.iteritems():
        if k == tricode:
            return team_db[k]
        elif ('{0} {1}'.format(team_db[k]['city'], team_db[k]['nick']) == tricode):
            return team_db[k]
    # if it gets this far, the team wasn't found in the database.
    raise error.DatabaseError(2)

def getAllTeams(prod_, name='tricode'):
    ''' Gets a list of all teams for a given production. '''
    team_db = getTeamDatabase(prod_)
    team_ls = []
    if name == 'tricode':
        for k in team_db:
            team_ls.append(k)
        return sorted(team_ls)
    elif name == 'full':
        for k,v in team_db.iteritems():
            team_ls.append('{0} {1}'.format(team_db[k]['city'], team_db[k]['nick']))
        return sorted(team_ls)
    elif name == 'city':
        for k,v in team_db.iteritems():
            team_ls.append('{0}'.format(team_db[k]['city']))
        return sorted(team_ls)
    elif name == 'nick':
        for k,v in team_db.iteritems():
            team_ls.append('{0}'.format(team_db[k]['nick']))
        return sorted(team_ls)


def getTeamColors(prod_, tricode):
    team = getTeam(prod_, tricode)
    ret_colors = {
        'primary': c4d.Vector(*convertColor(team['primary'])),
        'secondary': c4d.Vector(*convertColor(team['secondary'])),
        'tertiary': c4d.Vector(*convertColor(team['tertiary']))
        }
    return ret_colors


def isTricode(prod_, tricode):
    try:
        team = getTeam(prod_, tricode)
        return True
    except:
        return False


def convertColor(colorvec, to='float'):
    ''' Converts a color vector from 0-255 (int) to 0-1 (float) or back again. '''
    def _clamp(value):
        if value < 0: return 0
        if value > 255: return 255
    if (to == 'float'):
        r_ = (1.0/255) * colorvec[0]
        g_ = (1.0/255) * colorvec[1]
        b_ = (1.0/255) * colorvec[2]
        return (r_, g_, b_)
    if (to == 'int'):
        r_ = _clamp(int(255 * colorvec[0]))
        g_ = _clamp(int(255 * colorvec[1]))
        b_ = _clamp(int(255 * colorvec[2]))
        return (r_, g_, b_)
