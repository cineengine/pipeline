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

    core.changeColor('{0}_PRIMARY'.format(location.upper()), color_vectors['primary'], exact=False)
    core.changeColor('{0}_SECONDARY'.format(location.upper()), color_vectors['secondary'], exact=False)
    core.changeColor('{0}_TERTIARY'.format(location.upper()), color_vectors['tertiary'], exact=False)

    return True


def sortTagObject( name=None ):
    if not (name):
        name = c4d.RenameDialog('')
    if not (name == ''):
        tags = core.tag(typ=c4d.Tannotation, name=name)
    core.visibility(tags, v=False, r=False)
