import c4d

from pipeline.c4d import core
from pipeline.c4d import scene
from pipeline.c4d import database

reload(core)
reload(scene)
reload(database)


# TEAM AUTOMATION #################################################################################
def assignTeamColors( tricode, location, swap=False ):
    scene_data    = scene.getSceneData()
    color_vectors = database.getTeamColors(scene_data['Production'], tricode)

    core.changeColor('{}_PRIMARY'.format(location.upper()), color_vectors['primary'], exact=False)
    core.changeColor('{}_SECONDARY'.format(location.upper()), color_vectors['secondary'], exact=False)
    core.changeColor('{}_TERTIARY'.format(location.upper()), color_vectors['tertiary'], exact=False)

    return True
