import c4d
import os.path
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

def relinkTextures( prod_, migrate=False ):
    ''' Searches the scene for all referenced textures.  If any texture found already exists in the
        production's main texture repository, it changes the link to the production version instead.'''

    prod_tex_dir= os.path.join(database.getProduction(prod_)['assets'], 'TEXTURES')
    team_tex_dir= os.path.join(database.getProduction(prod_)['teams'], 'TEXTURES')
    # Build an array with all textured channels in the scene
    textures    = core.getSceneTextures()
    doc         = c4d.documents.GetActiveDocument()
    doc_tex_dir = os.path.join(doc.GetDocumentPath(), 'tex')
    relinked_tex= []
    new_tex     = []
    for tex in textures:
        # Extrapolating texture information
        shd, tex_path = tex
        tex_dir       = os.path.dirname(tex_path)
        tex_name      = os.path.basename(tex_path)
        # split the texture name and see if it contains a team tricode prefix
        tricode_      = tex_name.split('_')[0]
        is_team_tex   = database.isTricode(prod_, tricode_)
        # Check for an existing texture with the same name
        if (tex_dir == doc_tex_dir) and not (is_team_tex):
            # Non-team texture
            existing_tex = os.path.join(prod_tex_dir, tex_name)
            tricode_     = None
        elif (tex_dir == doc_tex_dir) and (is_team_tex):
            # Team texture (tricode prefix found)
            existing_tex = os.path.join(team_tex_dir, tricode_, tex_name)
        # If an existing texture is found:
        if (os.path.isfile(existing_tex)):
            shd[c4d.BITMAPSHADER_FILENAME] = str(existing_tex)
            # Tag the original for possible deletion
            relinked_tex.append((tex_path, tricode_))
        # If it's a texture not found in the database
        else: new_tex.append((tex_path, tricode))

    if (migrate):
        # List of 'new' team and generic textures (these textures were not found in production folders)
        new_team_tex = []
        new_generic_tex = []
        # Sort the 'new' textures into the empty lists by type (team and generic)
        for tex_path, tricode_ in unlinked:
            if (tricode_): new_team_tex.append(tex_path)
            else: new_generic_tex.append(tex_path)

        msg = 'New generic textures were found. Would you like to move these into the main textures folder?\n' +'\n'.join(new_generic_tex)
        c4d.gui.MessageDialog(msg, c4d.GEMB_OKCANCEL)

def removeUnlinkedTextures( unlinked_list ):
    team_list = []
    generic_list = []

    for tex_path, tricode in unlinked_list:
        print tex_path
        if (tricode): team_list.append(str(tex_path))
        else: generic_list.append(str(tex_path))

    generic_chk = c4d.gui.MessageDialog('\n'.join(generic_list), c4d.GEMB_OKCANCEL)
    team_chk    = c4d.gui.MessageDialog('\n'.join(team_list), c4d.GEMB_OKCANCEL)

