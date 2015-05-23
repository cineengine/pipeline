import nuke

SWAP_PATHS = {
    'R:/Projects/3013_ESPN_CFB_2015/04_Prod/ASSETS_LK/': 'Y:/Workspace/MASTER_PROJECTS/CFB_15/TOOLKIT/001_3D_ASSETS/',
    'R:/Projects/3013_ESPN_CFB_2015/04_Prod/ASSETS_ESPN/002_3D_TEAMS': 'Y:/Workspace/MASTER_PROJECTS/CFB_15/TOOLKIT/002_3D_TEAMS',
    'R:/Projects/3013_ESPN_CFB_2015/04_Prod/ASSETS_ESPN/000_ANIMATION': 'Y:/Workspace/MASTER_PROJECTS/CFB_15/PROJECTS/000_ANIMATION',
    'R:/Projects/3013_ESPN_CFB_2015/04_Prod/ASSETS_LK/TEXTURES/MATTES/': 'Y:/Workspace/MASTER_PROJECTS/CFB_15/TOOLKIT/001_3D_ASSETS/TEXTURES/MATTES/',
    'R:/Projects/3013_ESPN_CFB_2015/04_Prod/ASSETS_LK/3D_ENV/': 'Y:/Workspace/MASTER_PROJECTS/CFB_15/TOOLKIT/001_3D_ASSETS/3D_ENV/'
    }


def getAllNodesByType(typ=''):
    return_nodes = []

    if typ == '':
        return None

    for n in nuke.allNodes():
        if n.Class() == typ:
            return_nodes.append(n)

    return return_nodes


def remapReadNodes():
    read_nodes = getAllNodesByType('Read')

    for rn in read_nodes:
        read_path = rn['file'].getValue()

        for k,v in SWAP_PATHS.iteritems():
            if k in read_path:
                print read_path.replace(k,v)
                rn['file'].setValue(read_path.replace(k,v))


def remapPrecompNodes():
    precomp_nodes = getAllNodesByType('Precomp')

    for pc in precomp_nodes:
        pc_path = pc['file'].getValue()

        for k,v in SWAP_PATHS.iteritems():
            if k in pc_path:
                print pc_path.replace(k,v)
                pc['file'].setValue(pc_path.replace(k,v))


def remapAlembicNodes():
    readgeo_nodes = getAllNodesByType('ReadGeo2')

    for rg in readgeo_nodes:
        rg_path = rg['file'].getValue()

        for k,v in SWAP_PATHS.iteritems():
            if k in rg_path:
                print rg_path.replace(k,v)
                rg['file'].setValue(rg_path.replace(k,v))
