#    JSON Database operations for ESPN Animation projects pipeline
#    
#    Author:  Mark Rohrer
#    Contact: mark.rohrer@gmail.com
#    Version: 0.2
#    Date:    03\\22\\2016
#
#    
#
#    Features to be added: 

#
import c4d
import json
#
from pipeline.c4d import error


PRODUCTION_GLOBALS_DB = "v:\\dev\\pipeline\\c4d\\productions_db.json"


# GETTERS ##########################################################################################
def getProduction(prod_):
    ''' Gets a production's global variables from the database. '''
    merged_prod = {}
    with open(PRODUCTION_GLOBALS_DB) as stream:
        full_db = json.load(stream)
        for k,v in full_db.iteritems():
            if (k == 'DEFAULT'):
                default_prod = full_db[k]
            elif (k == prod_):
                request_prod = full_db[k]

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
    productions = []
    with open(PRODUCTION_GLOBALS_DB) as stream:
        full_db = json.load(stream)
        for k,v in full_db.iteritems():
            if (k == 'DEFAULT'):
                continue
            else:
                productions.append(k)
    return productions


