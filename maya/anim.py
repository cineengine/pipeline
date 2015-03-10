import re
import pymel.core as pm

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
        pm.waraning('Select a RIG node!')
        return

    # set up export paths
    scene         = project.SceneManager()
    export_folder = scene.maya_project_folder + '\\atom\\'
    export_file   = scene.project_name

    custom_string = pm.promptDialog(
        title='Custom name tag?',
        message='Add a custom tag to the filename?  i.e. \'LOGO\', \'CAM\', or whatev.',
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

    export_file += custom_string + '.atom'

    # select the whole heirarchy
    pm.select(heirarchy=True)

    # export the .atom for the selected heirarchy
    pm.exportSelected(
        (export_folder+export_file), 
        type='atomExport', 
        preserveReferences=True, 
        expressions=True
        )

    return True


def exportAbc(*a):
    # get selection
    sel = pm.ls(sl=True)[0]
    # get frame range
    start = str(pm.playbackOptions(q=True, min=True))
    end   = str(pm.playbackOptions(q=True, max=True))

    # check that the scene is controlled by the pipeline
    try: scene_controller = pm.PyNode('sceneControlObject')
    except: 
        pm.warning('Scene not set up for the pipeline.  Cannot export .abc')
        return

    # set up export paths
    scene         = project.SceneManager()
    export_folder = scene.maya_project_folder + '\\atom\\'
    export_file   = scene.project_name

    custom_string = pm.promptDialog(
        title='Custom name tag?',
        message='Add a custom tag to the filename?  i.e. \'LOGO\', \'CAM\', or whatev.',
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

    export_file += custom_string + '.abc'
    export_path += export_file

    pm.Mel.eval(
        "AbcExport -j -frameRange {0} {1} -dataFormat ogawa -root {2} -file {3};".format(
            start, end, sel, export_path)



def listAllRigNodes(*a):
    comp = re.compile('.:RIG$')
    return pm.ls(regex=comp)
