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



DATABASE_PATH = "Y:\\Workspace\\SCRIPTS\\pipeline\\database"
#DATABASE_PATH = "V:\\dev\\pipeline\\c4d"
#error.warning("Database is pathed locally. SETTINGS ARE NOT GLOBAL.")

# GETTERS ##########################################################################################
def getProduction(prod_):
    ''' Gets a production's global variables from the database. '''
    PRODUCTION_GLOBALS_DB = os.path.join(DATABASE_PATH, "productions_db.json")
    merged_prod = {}
    with open(PRODUCTION_GLOBALS_DB, 'r') as stream:
        full_db = json.load(stream)
        for k,v in full_db.iteritems():
            # default project is stored
            if (k == 'DEFAULT'):
                default_prod = full_db[k]
            # a specific project is requested
            elif (k == prod_):
                request_prod = full_db[k]
                request_prod['is_default'] = False
                # This block is for merging sub-dictionaries within the project entry
                # For now, it is hard-coded and must be updated with every sub-dictionary
                """
                raytrace = full_db['DEFAULT']['raytracing'].copy()
                raytrace.update(request_prod['raytracing'])
                request_prod['raytracing'] = raytrace
                """

            else: request_prod = {'is_default': True}
    # The project dictionaries only store the delta of data in the default dictionary
    # Therefore we merge the requested project dictionary over top of the default to create
    # a complete data set.
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

def exportRenderData():
    ''' Placeholder until i figure out how this might work. '''
    doc = c4d.documents.GetActiveDocument()
    rd  = doc.GetActiveRenderData()

    rdata = {
        c4d.RDATA_ANTIALIASING: rd[c4d.RDATA_ANTIALIASING],
        c4d.RDATA_AAFILTER: rd[c4d.RDATA_AAFILTER],
        c4d.RDATA_AATHRESHOLD: rd[c4d.RDATA_AATHRESHOLD],
        c4d.RDATA_AAMINLEVEL: rd[c4d.RDATA_AAMINLEVEL],
        c4d.RDATA_AAMAXLEVEL: rd[c4d.RDATA_AAMAXLEVEL],
        c4d.RDATA_AAOBJECTPROPERTIES: rd[c4d.RDATA_AAOBJECTPROPERTIES],
        c4d.RDATA_AAMIPGLOBAL: rd[c4d.RDATA_AAMIPGLOBAL],
        #c4d.RDATA_AASOFTNESS: rd[c4d.RDATA_AASOFTNESS],
        c4d.RDATA_RENDERENGINE: rd[c4d.RDATA_RENDERENGINE],
        c4d.RDATA_ACTIVEOBJECTONLY: rd[c4d.RDATA_ACTIVEOBJECTONLY],
        c4d.RDATA_AUTOLIGHT: rd[c4d.RDATA_AUTOLIGHT],
        c4d.RDATA_TEXTURES: rd[c4d.RDATA_TEXTURES],
        c4d.RDATA_TEXTUREERROR: rd[c4d.RDATA_TEXTUREERROR],
        c4d.RDATA_ENABLEBLURRY: rd[c4d.RDATA_ENABLEBLURRY],
        c4d.RDATA_VOLUMETRICLIGHTING: rd[c4d.RDATA_VOLUMETRICLIGHTING],
        c4d.RDATA_USELOD: rd[c4d.RDATA_USELOD],
        c4d.RDATA_SHOWHUD: rd[c4d.RDATA_SHOWHUD],
        c4d.RDATA_CACHESHADOWMAPS: rd[c4d.RDATA_CACHESHADOWMAPS],
        c4d.RDATA_ENABLESPD: rd[c4d.RDATA_ENABLESPD],
        c4d.RDATA_POSTEFFECTS_ENABLE: rd[c4d.RDATA_POSTEFFECTS_ENABLE],
        c4d.RDATA_RAYDEPTH: rd[c4d.RDATA_RAYDEPTH],
        c4d.RDATA_REFLECTIONDEPTH: rd[c4d.RDATA_REFLECTIONDEPTH],
        c4d.RDATA_SHADOWDEPTH: rd[c4d.RDATA_SHADOWDEPTH],
        c4d.RDATA_THRESHOLD: rd[c4d.RDATA_THRESHOLD],
        c4d.RDATA_LOD: rd[c4d.RDATA_LOD],
        c4d.RDATA_GLOBALBRIGHTNESS: rd[c4d.RDATA_GLOBALBRIGHTNESS],
        #c4d.RDATA_RENDERGAMMA: rd[c4d.RDATA_RENDERGAMMA],
        c4d.RDATA_MOTIONLENGTH: rd[c4d.RDATA_MOTIONLENGTH],
        c4d.RDATA_SAVEIMAGE: rd[c4d.RDATA_SAVEIMAGE],
        c4d.RDATA_PATH: rd[c4d.RDATA_PATH],
        c4d.RDATA_FORMAT: rd[c4d.RDATA_FORMAT],
        c4d.RDATA_SAVEOPTIONS: rd[c4d.RDATA_SAVEOPTIONS],
        c4d.RDATA_FORMATDEPTH: rd[c4d.RDATA_FORMATDEPTH],
        c4d.RDATA_NAMEFORMAT: rd[c4d.RDATA_NAMEFORMAT],
        c4d.RDATA_TRUECOLORDITHERING: rd[c4d.RDATA_TRUECOLORDITHERING],
        c4d.RDATA_ALPHACHANNEL: rd[c4d.RDATA_ALPHACHANNEL],
        c4d.RDATA_STRAIGHTALPHA: rd[c4d.RDATA_STRAIGHTALPHA],
        c4d.RDATA_SEPARATEALPHA: rd[c4d.RDATA_SEPARATEALPHA],
        c4d.RDATA_VRGENERATE: rd[c4d.RDATA_VRGENERATE],
        c4d.RDATA_HSTEPS: rd[c4d.RDATA_HSTEPS],
        c4d.RDATA_HSTART: rd[c4d.RDATA_HSTART],
        c4d.RDATA_HEND: rd[c4d.RDATA_HEND],
        c4d.RDATA_VSTEPS: rd[c4d.RDATA_VSTEPS],
        c4d.RDATA_VSTART: rd[c4d.RDATA_VSTART],
        c4d.RDATA_VEND: rd[c4d.RDATA_VEND],
        c4d.RDATA_VRDEFAULTX: rd[c4d.RDATA_VRDEFAULTX],
        c4d.RDATA_VRDEFAULTY: rd[c4d.RDATA_VRDEFAULTY],
        c4d.RDATA_PROJECTFILE: rd[c4d.RDATA_PROJECTFILE],
        c4d.RDATA_PROJECTFILETYPE: rd[c4d.RDATA_PROJECTFILETYPE],
        c4d.RDATA_PROJECTFILELOCAL: rd[c4d.RDATA_PROJECTFILELOCAL],
        c4d.RDATA_PROJECTFILEDATA: rd[c4d.RDATA_PROJECTFILEDATA],
        c4d.RDATA_XRES_VIRTUAL: rd[c4d.RDATA_XRES_VIRTUAL],
        c4d.RDATA_YRES_VIRTUAL: rd[c4d.RDATA_YRES_VIRTUAL],
        c4d.RDATA_PIXELRESOLUTION_VIRTUAL: rd[c4d.RDATA_PIXELRESOLUTION_VIRTUAL],
        c4d.RDATA_PROJECTFILESAVE: rd[c4d.RDATA_PROJECTFILESAVE],
        c4d.RDATA_XRES: rd[c4d.RDATA_XRES],
        c4d.RDATA_YRES: rd[c4d.RDATA_YRES],
        c4d.RDATA_FRAMESEQUENCE: rd[c4d.RDATA_FRAMESEQUENCE],
        c4d.RDATA_FRAMEFROM: rd[c4d.RDATA_FRAMEFROM],
        c4d.RDATA_FRAMETO: rd[c4d.RDATA_FRAMETO],
        c4d.RDATA_FRAMESTEP: rd[c4d.RDATA_FRAMESTEP],
        c4d.RDATA_FIELD: rd[c4d.RDATA_FIELD],
        c4d.RDATA_FRAMERATE: rd[c4d.RDATA_FRAMERATE],
        c4d.RDATA_LOCKRATIO: rd[c4d.RDATA_LOCKRATIO],
        c4d.RDATA_SIZEUNIT: rd[c4d.RDATA_SIZEUNIT],
        c4d.RDATA_PIXELRESOLUTION: rd[c4d.RDATA_PIXELRESOLUTION],
        c4d.RDATA_PIXELRESOLUTIONUNIT: rd[c4d.RDATA_PIXELRESOLUTIONUNIT],
        c4d.RDATA_FILMASPECT: rd[c4d.RDATA_FILMASPECT],
        c4d.RDATA_FILMPRESET: rd[c4d.RDATA_FILMPRESET],
        c4d.RDATA_PIXELASPECT: rd[c4d.RDATA_PIXELASPECT],
        c4d.RDATA_PRESET: rd[c4d.RDATA_PRESET],
        c4d.RDATA_MULTIPASS_SAVEIMAGE: rd[c4d.RDATA_MULTIPASS_SAVEIMAGE],
        c4d.RDATA_MULTIPASS_SAVEONEFILE: rd[c4d.RDATA_MULTIPASS_SAVEONEFILE],
        c4d.RDATA_MULTIPASS_ENABLE: rd[c4d.RDATA_MULTIPASS_ENABLE],
        c4d.RDATA_MULTIPASS_SAVEFORMAT: rd[c4d.RDATA_MULTIPASS_SAVEFORMAT],
        c4d.RDATA_MULTIPASS_SAVEOPTIONS: rd[c4d.RDATA_MULTIPASS_SAVEOPTIONS],
        c4d.RDATA_MULTIPASS_LIGHTS: rd[c4d.RDATA_MULTIPASS_LIGHTS],
        c4d.RDATA_MULTIPASS_FILENAME: rd[c4d.RDATA_MULTIPASS_FILENAME],
        c4d.RDATA_MULTIPASS_SAVEDEPTH: rd[c4d.RDATA_MULTIPASS_SAVEDEPTH],
        c4d.RDATA_MULTIPASS_LIGHTMODE: rd[c4d.RDATA_MULTIPASS_LIGHTMODE],
        c4d.RDATA_MULTIPASS_SUFFIX: rd[c4d.RDATA_MULTIPASS_SUFFIX],
        c4d.RDATA_MULTIPASS_SHADOWCORRECTION: rd[c4d.RDATA_MULTIPASS_SHADOWCORRECTION],
        c4d.RDATA_MULTIPASS_STRAIGHTALPHA: rd[c4d.RDATA_MULTIPASS_STRAIGHTALPHA],
        c4d.RDATA_RENDERDOODLE: rd[c4d.RDATA_RENDERDOODLE],
        c4d.RDATA_INCLUDESOUND: rd[c4d.RDATA_INCLUDESOUND],
        c4d.RDATA_GLOBALSAVE: rd[c4d.RDATA_GLOBALSAVE],
        c4d.RDATA_HELPTEXT: rd[c4d.RDATA_HELPTEXT],
        c4d.RDATA_SAVECALLBACK_FUNC: rd[c4d.RDATA_SAVECALLBACK_FUNC],
        c4d.RDATA_SAVECALLBACK_USERDATA: rd[c4d.RDATA_SAVECALLBACK_USERDATA],
        c4d.RDATA_OPTION_TRANSPARENCY: rd[c4d.RDATA_OPTION_TRANSPARENCY],
        c4d.RDATA_OPTION_REFRACTION: rd[c4d.RDATA_OPTION_REFRACTION],
        c4d.RDATA_OPTION_REFLECTION: rd[c4d.RDATA_OPTION_REFLECTION],
        c4d.RDATA_OPTION_SHADOW: rd[c4d.RDATA_OPTION_SHADOW],
        c4d.RDATA_LIMITREFLECTION: rd[c4d.RDATA_LIMITREFLECTION],
        c4d.RDATA_LIMITSHADOW: rd[c4d.RDATA_LIMITSHADOW],
    }

    for k in rdata:
        if not (type(rdata[k]) == int or\
                type(rdata[k]) == float or\
                (rdata[k])     == None or\
                type(rdata[k]) == bool):
            print k, rdata[k].GetName()

def isTricode(prod_, tricode):
    try:
        team = getTeam(prod_, tricode)
        return True
    except:
        return False

def makeTeamFolders(prod_):
    team_folder = getProduction(prod_)['teams']
    for t in getAllTeams(prod_):
        tri_folder = os.path.join(team_folder, t)
        tex_folder = os.path.join(tri_folder, 'tex')
        if not os.path.isdir(tri_folder):
            os.makedirs(tri_folder)
        if not os.path.isdir(tex_folder):
            os.makedirs(tex_folder)
    return True

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
