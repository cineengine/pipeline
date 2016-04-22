import c4d
import os.path
from c4d import gui

from pipeline.c4d import core
from pipeline.c4d import scene
from pipeline.c4d import database

reload(core)
reload(scene)
reload(database)

TRUNCATE_PATH = "\\\\cagenas.bst.espn.pvt\\cagenas\\Workspace\\MASTER_PROJECTS\\"
CONVERT_PATH  = ["Y:\\", "\\\\cagenas.bst.espn.pvt\\cagenas\\"]

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

def relinkTextures( migrate=False ):
    ''' Searches the scene for all referenced textures.  If any texture found already exists in the
        production's main texture repository, it changes the link to the production version instead.
        Optional migrate flag will prompt the user to select which remaining textures they would like
        moved & relinked to production folders.'''
    prod_ = 'NBA_2016'
    prod_tex_dir= os.path.join(database.getProduction(prod_)['assets'], 'TEXTURES')
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
        if (is_team_tex): team_tex_dir = os.path.join(database.getProduction(prod_)['teams'], tricode_, 'tex')
        else: tricode_ = None
        # Check for an existing texture with the same name
        if not (is_team_tex):
            existing_tex = os.path.join(prod_tex_dir, tex_name)
        elif (is_team_tex):
            existing_tex = os.path.join(team_tex_dir, tex_name)
        # If an existing texture is found:
        if (os.path.isfile(existing_tex)):
            # RELINK THE TEXTURE
            shd[c4d.BITMAPSHADER_FILENAME] = str(existing_tex)
            # Tag the original for possible deletion
            relinked_tex.append((tex_path, tricode_, shd))
        # If it's a texture not found in the database
        else: new_tex.append((tex_path, tricode_, shd))

    if (migrate):
        # List of 'new' team and generic textures (these textures were not found in production folders)
        # Sort the 'new' textures into the empty lists by type (team and generic)
        test = TextureMigrateWindow(new_tex)
        test.Open(dlgtype=c4d.DLG_TYPE_MODAL, defaultw=800, defaulth=50)

### UI OBJECTS ###################################################################################
class TextureMigrateWindow(gui.GeDialog):
    def __init__(self, texture_list):
        # Texture migration UI values
        self.INSTRUCTIONS = 90000
        self.CHKBOX_START = 10000
        self.CHKBOX_DATA  = {}
        self.BUTTON_OK    = 20000
        self.BUTTON_CANCEL= 20001

        i = self.CHKBOX_START
        for tex_path, tricode, shd in texture_list:
            self.CHKBOX_DATA[i] = [tex_path, tricode, shd]
            i+=1

        self.left   = c4d.BFH_LEFT
        self.center = c4d.BFH_CENTER
        self.right  = c4d.BFH_RIGHT

    def CreateLayout(self):
        self.SetTitle('Migrate Textures')
        self.GroupBegin(1000, flags=c4d.BFH_SCALEFIT, rows=1, cols=1, title="Instructions")
        self.GroupBorder(c4d.BORDER_THIN_IN)
        self.GroupBorderSpace(5,5,5,5)
        msg = """Select the textures you would like to move into production global folders.
All moved textures will be relinked in your scene.  Textures left unchecked will 
remain where they are.

NOTE: Team textures (identified by TRICODE_ prefix) will be moved to the team's asset /tex/ folder.
"""
        self.AddMultiLineEditText(self.INSTRUCTIONS, c4d.BFH_SCALEFIT, c4d.BFV_SCALEFIT, inith=60, style=c4d.DR_MULTILINE_READONLY)
        #self.Enable(self.INSTRUCTIONS, False)
        self.SetString(self.INSTRUCTIONS, msg)
        self.GroupEnd()

        self.GroupBegin(1001, c4d.BFH_SCALE, 2, 0, initw=800, title='Textures to check-in')
        self.GroupBorder(c4d.BORDER_THIN_IN)
        self.GroupBorderSpace(5,5,5,5)
        for i in range(len(self.CHKBOX_DATA)):
            i += self.CHKBOX_START
            name = os.path.relpath(self.CHKBOX_DATA[i][0].replace(CONVERT_PATH[0], CONVERT_PATH[1]), TRUNCATE_PATH.replace(CONVERT_PATH[0], CONVERT_PATH[1]))
            self.AddCheckbox(i, self.left, name='', initw=20, inith=0)
            self.AddStaticText(1002, self.left, name=name)
        self.GroupEnd()

        self.GroupBegin(1002, c4d.BFH_RIGHT, 2, 1)
        self.AddButton(self.BUTTON_OK, c4d.BFH_RIGHT, inith=30, name='Migrate Textures')
        self.AddButton(self.BUTTON_CANCEL, c4d.BFH_RIGHT, inith=30, name='Cancel')
        self.GroupEnd()
        return True

    def Command(self, id, msg):
        if (id==self.BUTTON_OK):
            self.run()
            self.Close()
            relinkTextures()
        return True

    def run(self):
        for i in range(len(self.CHKBOX_DATA)):
            i += self.CHKBOX_START
            chk = self.GetBool(i)
            if (chk):
                tex_path, tricode, shd = self.CHKBOX_DATA[i]
                if not (tricode):
                    print 'copying', tex_path, 'to TEXTURES'
                    #os.rename(tex_path, os.path.join(database.getProduction('NBA_2016')['assets'], 'TEXTURES'))
                elif (tricode):
                    print 'copying', tex_path, 'to TEAM FOLDER'
                    #os.rename(tex_path, os.path.join(database.getProduction('NBA_2016')['teams'], tricode, 'tex'))
