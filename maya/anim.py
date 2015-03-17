# Built-in modules
import re
from os.path import exists

# Maya-specific modules
import pymel.core as pm

# Internal modules
from pipeline.maya import project


def exportAtom(*a):
    # get selection
    sel = pm.ls(sl=True)[0]

    # check that the scene is controlled by the pipeline
    try: scene_controller = pm.PyNode('sceneControlObject')
    except: 
        pm.warning('Scene not set up for the pipeline.  Cannot export .atom')
        return
    # check that a rig node is selected
    if sel not in listAllRigNodes(): 
        pm.warning('Select a RIG node!')
        return

    msg = 'Add a custom tag to the filename?  i.e. \'LOGO\', \'CAM\', or whatev.'
    export_path = getExportPath('atom', msg)

    # select the whole heirarchy
    pm.select(heirarchy=True)

    # export the .atom for the selected heirarchy
    pm.exportSelected(
        export_path, 
        type='atomExport', 
        preserveReferences=True, 
        expressions=True
        )

    pm.select(sel)
    return True


def exportAbc(*a):
    # get selection
    sel = pm.ls(sl=True)[0]
    # get frame range
    start = str(pm.playbackOptions(q=True, min=True))
    end   = str(pm.playbackOptions(q=True, max=True))

    msg = 'Add a custom tag to the filename?  i.e. \'LOGO\', \'CAM\', or whatever it is you\'re exporting.'
    export_path = getExportPath('abc', msg)

    pm.Mel.eval(
        "AbcExport -j -frameRange {0} {1} -dataFormat ogawa -root {2} -file {3};".format(
            start, end, sel, export_path))
    return


def getExportPath(filetype, message, override_name=False):

    # check that the scene is controlled by the pipeline
    try: scene_controller = pm.PyNode('sceneControlObject')
    except: 
        pm.warning('Scene not set up for the pipeline.  Cannot use export tools.')
        return False

    # set up export paths
    scene         = project.SceneManager()
    export_folder = str(scene.maya_project_folder) + '\\{0}\\'.format(filetype)
    export_file   = scene.project_name

    if override_name:
        export_file += '.{0}'.format(filetype)

    else:
        custom_string = pm.promptDialog(
            title='Custom name tag?',
            message=message,
            text='',
            b=['OK', 'No'],
            db='OK',
            cb='No',
            ds='No'
            )
        if custom_string == 'OK':
            custom_string = pm.promptDialog(q=True, text=True)
        else:
            custom_string = ''
        export_file += custom_string + '.{0}'.format(filetype)

    return export_folder + export_file


def bakeCamera( exp=False, *args, **kwargs ):
    """Duplicates a baked version of a camera.  Expects a valid camera transform node."""
    # Frame range
    frame_range = ( 
        pm.playbackOptions( q=True, min=True ), 
        pm.playbackOptions( q=True, max=True )
        )
    
    # Duplicate the camera
    dup_cam = pm.duplicate( cam, name=(cam.name() + '_Baked') )[0]
    
    # Parent new camera to world.
    try: pm.parent(dup_cam, w=True)
    except RuntimeError: pass
    
    # Constrain new camera to old
    const = pm.parentConstraint( cam, dup_cam, mo=True )
    
    # Bake it
    pm.bakeResults( dup_cam, t=frame_range )

    # Delete the constraint
    pm.delete(const)

    return dup_cam


def exportCamera(*a):
    # get selection
    sel = pm.ls(sl=True)[0]

    # find the first camera
    children = sel.getChildren()
    for child in children:
        if type(child) is not pm.nodetypes.Camera:
            continue
        else:
            break

    # bake it
    camera = bakeCamera(child)
    
    # get the scene export path
    export_path = getExportPath('fbx', '', override_name='cam')

    # select and export camera
    pm.select(camera)
    pm.exportSelected(export_path, type='fbx')
    pm.warning('Successfully exported camera  {0}  to  {1}.'.format(camera, export_path))
    return True


def playblast(*a):
    # Frame range
    frame_range = ( 
        pm.playbackOptions( q=True, min=True ), 
        pm.playbackOptions( q=True, max=True )
        )

    out_path = "c:\\temp\\temp.mov"

    if exists(out_path):
        versionup_out_path.split('.')[0]

    pm.Mel.eval('setCurrentFrameVisibility(1);')
    pm.playblast(
        startTime   = frame_range[0],
        endTime     = frame_range[1],
        filename    = out_path,
        format      = 'qt',
        compression = 'H.264',
        orn         = False,
        width       = 960,
        height      = 540,
        percent     = 100,
        quality     = 70,
        clearCache  = True
        )
    


def listAllRigNodes(*a):
    comp = re.compile('.:RIG$')
    return pm.ls(regex=comp)
