import c4d

from pipeline.c4d import core
from pipeline.c4d import scene
from pipeline.c4d import database

reload(core)
reload(scene)
reload(database)

TEAM_MATERIALS = [
    '{}_PRIMARY',
    '{}_SECONDARY',
    '{}_TERTIARY'
    ]

# TEAM AUTOMATION #################################################################################
def assignTeamColors( tricode, location, swap=False ):
    scene_data    = scene.getSceneData()
    color_vectors = database.getTeamColors(scene_data['Production'], tricode)

    core.changeColor('{}_PRIMARY'.format(location), color_vectors['primary'])
    core.changeColor('{}_SECONDARY'.format(location), color_vectors['secondary'])
    core.changeColor('{}_TERTIARY'.format(location), color_vectors['tertiary'])

    return True
