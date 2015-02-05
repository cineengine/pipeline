# Built-in modules
import os

# Maya-specific modules
import maya.cmds as cmds
import pymel.core as pm
import pymel.core.system as pmsys

# ESPN-specific modules
#import pipeline.maya.submit as submit

class SceneManager(object):
    def __init__(self, animation_base_dir, folder_structure):
        # The base path for all projects
        self.base_path = animation_base_dir
        # Dictionary for this project's folder structure.  Found in pipeline.<project_name> module.
        self.folder_structure = folder_structure

        # The name of the project.  
        # Ex: "CFB_S_REJOIN_01"
        self.project_name = ''
        # The name of the scene (including variation).  This is what scene files, render folders, etc will be named.  
        # Ex: "CFB_S_REJOIN_01_GAMEDAY"
        self.scene_name = ''

        # The project folders of the scene file.  
        # Ex: "V:\CFB_S_REJOIN_01\"
        self.project_folder = ''
        # Ex: "V:\CFB_S_REJOIN_01\maya\"
        self.maya_project_folder = ''
        # Ex: "V:\CFB_S_REJOIN_01\maya\backup\"
        self.backup_folder = ''

        # The full paths relating to the scene file.
        # Ex: "V:\CFB_S_REJOIN_01\maya\scenes\CFB_S_REJOIN_01_GAMEDAY.mb"
        self.full_path = ''
        # The full path of the next queued backup of this scene file.
        # Ex: "V:\CFB_S_REJOIN_01\maya\backup\CFB_S_REJOIN_01_GAMEDAY_0002.mb"
        self.backup_path = ''

        self._initCheck()

    def __repr__(self, *a):
        print '\n'
        print 'SCENE MANAGER REPORT ::'
        print 'Project Name: '   + self.project_name
        print 'Scene Name :  '   + self.scene_name
        print 'Project Folder: ' + self.maya_project_folder
        print 'Full Path : '     + self.full_path
        print 'Next Backup '     + self.backup_path
        print '\n'
        return ' '

    class NameWindow(pm.uitypes.Window):
        def __init__(self):
            self.wh = (480,210)
            self.setTitle('Select a name for this scene')
            self.setToolbox()
            self.setResizeToFitChildren(1)
            self.setSizeable(0)
            self.setWidth(self.wh[0])
            self.setHeight(self.wh[1])

            self.project_str = scene.project_name
            print scene.project_name

            main_layout = pm.formLayout(p=self)
            column      = pm.columnLayout(p=main_layout)
            proj_text   = pm.text(label='seriously whta the fuck')

            main_layout.redistribute()
            self.show()


    def _initCheck(self, *a):
        ''' Checks the status of the scene.  If the scene has a maya sceneControlObject, it updates the 
            pre-existing python SceneManager object.  (Such as when a pipeline scene is opened.)
            If it is a clean / non-pipelined scene, it sets up the scene for controlling.'''
        try:
            # If there's a scene controller,
            self.scene_controller = pm.PyNode('sceneControlObject')
            # ..import metadata from the node
            self._updateIn()
            # Print a report
            print self
            return 1

        except pm.MayaNodeError:
            # If there's no scene controller, try to initialize the scene
            success = self._initScene()
            # Print a report if it worked
            if success:
                print self
                return 2
            else:
                pm.warning('SCENE MANAGER REPORT :: FAILED :: Scene failed to initialize. Ask Mark.')
                return 0

    def _initScene(self, *a):
        ''' If this is a new scene, organize it into a project.
            If this is a pre-existing scene not yet conformed to the project structure, 
            it will attempt to reconcile it. '''

        self.version = 1.0

        # CREATE SCENE CONTROLLER OBJECT.  This will store information about the scene
        # to simplify parsing when opening/saving the scene in the future.
        self.scene_controller = pm.createNode('locator', name='sceneControlObject')
        pm.lockNode(self.scene_controller, lock=False)
        # Add custom attributes
        self.scene_controller.addAttr('ProjectName', dt='string')
        self.scene_controller.addAttr('SceneName', dt='string')
        self.scene_controller.addAttr('CustomTag', dt='string')
        self.scene_controller.addAttr('Version', at='float')
          # Set initialized custom attributes
        self.scene_controller.attr('Version').set(self.version)
        # Lock the node
        pm.lockNode(self.scene_controller, lock=True)
        

        # NAME PROMPT
        # Prompt for a project name
        name_query = pm.promptDialog(
            title='New Project Name',
            message='What project folder should this go in? i.e. \'CFB_S_REJOIN_01\'\nNote: Do not include \'_GAMEDAY\' or any other descriptors in this step.',
            text='CFB_',
            b=['OK', 'Cancel'],
            db='OK',
            cb='Cancel',
            ds='Cancel'
            )
        # Abort on cancel
        if name_query == 'Cancel':
            return False
        # Populate the value
        else: 
            self.project_name = pm.promptDialog(q=True, text=True)

        # Prompt for a custom tag for the scene        
        custom_string = pm.promptDialog(
            title='Custom name tag?',
            message='Do you want to create a custom descriptor for the scene file?  i.e. \'GAMEDAY\', \'PRIMETIME\', etc.',
            text='',
            b=['OK', 'No'],
            db='OK',
            cb='No',
            ds='No'
            )
        if custom_string == 'OK':
            self.custom_string = pm.promptDialog(q=True, text=True)
        else:
            self.custom_string = ''


        # INITIALIZATION TREE:
        # Name the scene and begin init process
        print '\nCREATING SCENE ... ' + self.scene_name 
        self._nameScene()
        
        # Set initialized values on the sceneController and generate full file paths
        print '\nUpdating scene controller ...'
        self._pushPull()

        # Check if the project exists, and if any scene files exist (and if so, get the next available variant)
        project_exists, scene_exists = self._isProject()

        # Either nothing exists, we make everything, save the scene, and we're done
        if not project_exists:
            try:
                print self.project_folder
                print '\nMaking folders ...'
                self._makeFolders()
                print '\nMaking project workspace ...'
                self._makeProject()
                print '\nSetting maya project ...'
                self.setProject()
                print '\nSaving file ...'
                self.save()
                print '\n... Done!'
                return True
            except: return False

        # Or: The project exists but this variant hasn't been saved yet, so just save, and we're done.
        elif project_exists and not scene_exists:
            try:
                self.setProject()
                self.save()
                return True
            except: return False

        # Or: Even the variant already exists, so we have a decision tree for the user.
        elif scene_exists:
            query = pm.confirmDialog(
                title='New Version?',
                message='There is already a file called ' + self.name + '.mb. Select an option below.',
                buttons=['Backup & Overwrite', 'New Version', 'Cancel'],
                db='New Variant',
                cb='Cancel',
                ds='Cancel'
                )
            # 3A
            # Overwrite means we confirm it and just save without incrementing anything
            if query == 'Backup & Overwrite':
                confirm = pm.confirmDialog(
                    title='Are you sure?',
                    message='Are you sure you want to overwrite this scene? DO NOT choose this option if things have already been rendered, unless you know what you\'re doing',
                    buttons=['Yes', 'No'],
                    db='Yes',
                    cb='Cancel',
                    ds='Cancel'
                    )
                if confirm:
                    self.save()
            # 3B
            # New variant means we need to increment the variable and save the scene
            elif query == 'New Version':
                self._rename()
                self.setProject()
                self.save()

            # Cleanup on abort
            else:
                try: pm.delete(self.scene_controller)
                except: pass
                return False

        else:
            try: pm.delete(self.scene_controller)
            except: pass
            return False

    def _isProject(self):
        ''' Checks whether a passed path/folder exists and has a maya project definition (workspace.mel). 
            Returns: Tuple ((0, 0): Doesn't exist, 
                            (1, 0): Folder exists but no variations (files) exist,
                            (1, 1): Folder and scene already exist .. prompt for a new name / overwrite '''
        folder_exists = os.path.exists(self.project_folder)
        scene_exists = os.path.exists(self.full_path)

        # If the project folder doesnt exist, just escape out immediately
        if not folder_exists:
            return (False, None)

        elif folder_exists and not scene_exists:
            return (True, None)

        elif scene_exists:
            return (True, True)

    def _incrVersion(self, version_only=False):
        ''' This function recursively increments versions attempting to find the next available file name for a
            backup of the scene file. 

            Note that unlike _incrVariant(), this function will always change values in the SceneControl object,
            if it determines that the currently queued backup has already been saved.'''
        file_name = self.backup_folder + self.scene_name + '_' + self._formatVersion() + '.mb'

        if os.path.exists(file_name):
            self.version += 1
            file_name = _incrVersion()
        
        if version_only:
            return self.version
        else:
            self.backup_path = file_name 
            return file_name

    def _formatVersion(self):
        return str(int(self.version)).zfill(4)
    
    def _nameScene(self):
        if self.custom_string != '':
            self.scene_name = self.project_name + '_' + self.custom_string
        else: 
            self.scene_name = self.project_name

    def rename(self):
        prompt = pm.promptDialog(
                    title='Rename Scene',
                    message='Enter new descriptor tag (i.e. PRIMETIME)',
                    text='',
                    button=['OK','Cancel'],
                    db='OK',
                    cb='Cancel',
                    ds='Cancel'
                    )

        if prompt == 'OK':
            self.custom_string = pm.promptDialog(q=True, text=True)
            self._nameScene()
            self._pushPull()
            self.save()
        else:
            return False


    def _updateOut(self):
        ''' Updates the maya sceneControlObject with any internal changes made to the python SceneManager.'''
        # Set all the values to be stored on the sceneControlObject
        self.scene_controller.attr('Version').set(self.version)
        #self.scene_controller.attr('Variation').set(self.variant)
        self.scene_controller.attr('SceneName').set(self.scene_name)
        self.scene_controller.attr('ProjectName').set(self.project_name)
        self.scene_controller.attr('CustomTag').set(self.custom_string)

    def _updateIn(self):
        ''' Updates the python SceneControl object with any changes made to the sceneControlObject (such as 
            when a new scene is opened.) '''
        # Getting attrs from sceneControlObject
        self.scene_name    = self.scene_controller.attr('SceneName').get()
        self.project_name  = self.scene_controller.attr('ProjectName').get()
        self.version       = self.scene_controller.attr('Version').get()
        #self.variant       = self.scene_controller.attr('Variation').get()
        self.custom_string = self.scene_controller.attr('CustomTag').get()
        # Combining project name and variant to create a scene name
        self._nameScene()

        # Setting new values (i.e. doing the business)
        self.project_folder      = self.base_path + self.project_name + '\\'
        self.maya_project_folder = self.project_folder + 'maya\\'
        self.backup_folder       = self.maya_project_folder + 'backup\\'
        self.full_path           = self.maya_project_folder + 'scenes\\' + self.scene_name + '.mb'
        self.backup_path         = self._incrVersion()
        return True

    def _pushPull(self):
        self._updateOut()
        self._updateIn()

    def _makeProject(self):
        ''' Make a new workspace definition file (workspace.mel) for this scene, if needed. '''
        # First, check that it doesn't already exist
        if os.path.exists(self.maya_project_folder + '\\workspace.mel'):
            #print 'Loaded workspace.mel from ' + self.base_path + '\\maya\\'
            return True
        # open the default workspace template
        with open('\\\\cagenas\\workspace\\scripts\\maya\\workspace.mel', 'r') as workspace:
            workspace_lines = workspace.readlines()
        # modify the line for render output
        workspace_lines[56] = "workspace -fr \"images\" \"" + self.project_folder.replace('\\','/') + "/render_3d\";\n"
        # and save it to the new project folder
        with open(self.maya_project_folder + 'workspace.mel', 'w') as workspace:
            workspace.writelines(workspace_lines)
        print 'Created workspace.mel for ' + self.maya_project_folder
        return True

    def _makeFolders(self):
        ''' Make the folder template for a deliverable (meta-project -- including nuke, ae, etc).
            Note: this should probably be moved in later versions.'''
        main_folder = self.base_path + self.project_name
        if not os.path.exists(main_folder):
            os.mkdir(main_folder)

        for k,v in self.folder_structure.iteritems():
            this_folder = main_folder +"\\"+ k +"\\"
            print this_folder
            if not os.path.exists(this_folder):
                os.mkdir(this_folder) 
            if v != []:
                for _v in v:
                    sub_folder = this_folder + _v
                    print sub_folder
                    os.mkdir(sub_folder)
        return True

    def save(self, *a):
        ''' Saves a backup of the current scene and overwrites it as a master scene file. '''
        if not self.scene_controller:
            pm.warning('Can\'t use this command until you\'ve set up the scene in the pipeline.')

        # Save the backup
        self.backup_path = self._incrVersion()
        try:
            cmds.file(rename=self.backup_path)
            cmds.file(save=True, type='mayaBinary')
        except:
            pm.warning('Failed to save backup!!  Check your scene file name and save an emergency local backup.')
        # Save the master
        try:
            cmds.file(rename=self.full_path)
            cmds.file(save=True, type='mayaBinary')
        except:
            pm.warning('Failed to save new master scene!  Save an emergency backup of this scene and let Mark know.')

        return True

    def setProject(self, *a):
        ''' Sets the current workspace to the controlled scene's project path.'''
        try:
            pmsys.Workspace.open(self.maya_project_folder)
            print 'Set project to: ' + self.maya_project_folder
            return True
        except:
            pm.warning('Failed to set the specified project.  It probably doesn\'t exist')
            return False
"""
    def open(self, *a):
        ''' Opens a scene browsing UI and sets the associated project. '''
        new_file = pm.fileDialog2(fm=1, ds=1, dir=self.base_path)
        if not new_file:
            return None
        try:
            pm.file(new_file, open=True)
        	self._updateIn()
        except:
            pm.warning('Could not open file: ' + new_file)

    def submit(self, *a):
        ''' Submits the current scene to the render farm. '''
        sub = submit.RenderSubmitWindow()
        return True
"""
