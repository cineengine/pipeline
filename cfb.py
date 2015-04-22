##############################################################################
###                  PROJECT-SPECIFIC GLOBAL VARIABLES:                    ###
###            COLLEGE FOOTBALL 2015 PLAYOFFS / REGULAR SEASON             ###
##############################################################################

# version tag
version = """
version 1.0.2
April 17th, 2015
"""

# Main project directory
PROJECT_BASE_DIR = "Y:\\Workspace\\MASTER_PROJECTS\\CFB_15\\"

# Asset directories
MAIN_ASSET_DIR = PROJECT_BASE_DIR + "TOOLKIT\\001_3D_ASSETS\\"
TEAMS_ASSET_DIR = PROJECT_BASE_DIR + "TOOLKIT\\002_3D_TEAMS\\"
#TEMPLATE_ASSET_DIR = PROJECT_BASE_DIR + "TOOLKIT\\004_TEMPLATES\\"
ANIMATION_PROJECT_DIR = PROJECT_BASE_DIR + "PROJECTS\\000_Animation\\"

# Database locations
TEAM_DATABASE = "Y:\\Workspace\MASTER_PROJECTS\\CFB_15\\TOOLKIT\\097_SCRIPTS\\pipeline\\database\\cfb_teams.yaml"
#SORTING_DATABASE = "Y:\\Workspace\MASTER_PROJECTS\\CFB_15\\TOOLKIT\\097_SCRIPTS\\pipeline\\database\\cfb_sorting.yaml"
SORTING_DATABASE = "V:\\dev\\pipeline\\database\\cfb_sorting.yaml"
TEMPLATES_DATABASE = "Y:\\Workspace\MASTER_PROJECTS\\CFB_15\\TOOLKIT\\097_SCRIPTS\\pipeline\\database\\cfb_templates.yaml"

# Factory location
FACTORY_LIGHT_RIG = MAIN_ASSET_DIR + "\\000_FACTORY\\FACTORY.mb"

# Location for a default workspace.mel file
DEFAULT_WORKSPACE_MEL = "\\\\cagenas\\workspace\\scripts\\maya\\workspace.mel"

# Folder structure
FOLDER_STRUCTURE = {
        'ae': [],
        'mari': [],
        'maya': ['scenes', 'backup', 'atom'],
        'nuke': [],
        'c4d': [],
        'render_3d': [],
        'render_2d': ['prerenders'],
        'qt': [],
        'abc': [],
        'cam': []
        }

NAMESPACES = [
        'CFB_LOGO',
        'HOMELOGO',
        'AWAYLOGO',
        'HOMESIGN',
        'AWAYSIGN',
        'LAYOUT',
        'CAM',
        'CLOTH',
        'FACTORY'
        ]


FRAMEBUFFERS = {
    'beauty':[
        'reflection',
        'specular',
        'diffuse',
        'SSS',
        'lighting',
        'selfIllum',
        'GI',
        'totalLight'
        ],
    'team_logo':[
        'reflection',
        'specular',
        'diffuse',
        'SSS',
        'lighting'
        ],
    'sign':[
        'reflection',
        'specular',
        'diffuse',
        'lighting',
        'selfIllum'
        ],
    'utility':[
        'zDepth',
        'normals',
        'UV',
        'AO',
        'PPW',
        'MV'
        ],
    'matte':['']
    }