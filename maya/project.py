# Built-in modules
import os

# Maya-specific modules
import pymel.core as pm
import pymel.core.system as pmsys

# ESPN-specific modules
import pipeline.maya.submit as submit


class SceneManager(object):
	def __init__(self, animation_base_dir, folder_structure):
		# The base path for all projects
		self.base_path = animation_base_dir
		# Dictionary for this project's folder structure.  Found in pipeline.<project_name> module.
		self.folder_structure = folder_structure

		# The name of the project.  
		# Ex: "CFB_S_GAMEDAY_REJOIN"
		self.project_name = ''
		# The name of the scene (including variation).  
		# Ex: "CFB_S_GAMEDAY_REJOIN_01"
		self.scene_name = ''

		# The project folders of the scene file.  
		# Ex: "V:\CFB_S_GAMEDAY_REJOIN\"
		self.project_folder = ''
		# Ex: "V:\CFB_S_GAMEDAY_REJOIN\maya\"
		self.maya_project_folder = ''
		# Ex: "V:\CFB_S_GAMEDAY_REJOIN\maya\backup\"
		self.backup_folder = ''

		# The full paths relating to the scene file.
		# Ex: "V:\CFB_S_GAMEDAY_REJOIN\maya\scenes\CFB_S_GAMEDAY_REJOIN_01.mb"
		self.full_path = ''
		# The full path of the next queued backup of this scene file.  
		# Ex: "V:\CFB_S_GAMEDAY_REJOIN\maya\backup\CFB_S_GAMEDAY_REJOIN_01_0002.mb"
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

	def _initCheck(self, *a):
		''' Checks the status of the scene.  If the scene has a maya sceneControlObject, it updates the 
			pre-existing python SceneManager object.  If it is a clean / non-controlled scene, it sets 
			up the scene for controlling.'''
		try:
			self.scene_controller = pm.PyNode('sceneControlObject')
			self._updateIn()
			print self
			return 1

		except pm.MayaNodeError:
			success = self._initScene()
			print self
			return 2
			if not success:
				pm.warning('SCENE MANAGER REPORT :: FAILED :: Scene failed to initialize. Ask Mark.')
				return 0

	def _initScene(self, *a):
		''' If this is a new scene, organize it into a project.
			If this is a pre-existing scene not yet conformed to the project structure, 
			it will attempt to reconcile it. '''

		self.version = 1.0
		self.variant = 1.0

		# Create scene controller object.  This will store information about the scene
		# to simplify parsing when opening/saving the scene in the future.
		self.scene_controller = pm.createNode('locator', name='sceneControlObject')
		pm.lockNode(self.scene_controller, lock=False)
		# Add custom attributes
		self.scene_controller.addAttr('Deliverable', dt='string')
		self.scene_controller.addAttr('SceneName', dt='string')
		self.scene_controller.addAttr('Variation', at='float')
		self.scene_controller.addAttr('Version', at='float')
		# Set initialized custom attributes
		self.scene_controller.attr('Variation').set(self.version)
		self.scene_controller.attr('Version').set(self.variant)
		# Lock the node
		pm.lockNode(self.scene_controller, lock=True)
		
		# Prompt for a project name
		name_query = pm.promptDialog(
			title='New Project / Deliverable Type Name',
			message='Which deliverable does this scene correspond to?',
			text='CFB_',
			b=['OK', 'Cancel'],
			db='OK',
			cb='Cancel',
			ds='Cancel'
			)

		# Abort on cancel
		if name_query == 'Cancel':
			return False

		# Continue populating attributes
		else: 
			self.project_name = pm.promptDialog(q=True, text=True)
			# Set initialized values on the sceneController
			print 'Updating scene controller ...'
			self._updateOut()

		# Check if the project exists, and if any scene files exist (and if so, get the next available variant)
		exists, next_variant = self._isProject()

		# Nothing exists, make everything, save the scene, and we're done
		if not exists:
			try:
				print self.project_folder
				print 'Making folders ...'
				self._makeFolders()
				print 'Making project workspace ...'
				self._makeProject()
				print 'Setting maya project ...'
				self.setProject()
				print 'Saving file ...'
				self.save()
				return True
			except:	return False

		# The project exists but there's nothing saved, so just save, and we're done.
		elif exists and not next_variant:
			try:
				self.setProject()
				self.save()
				return True
			except: return False

		# The variant already exists, so we have a decision tree for the user.
		elif next_variant:
			query = pm.confirmDialog(
				title='New Variant?',
				message='There is already a file called ' + self.name + '_' + self._formatVariant(2) + '.mb. Select an option below.',
				buttons=['Backup & Overwrite', 'New Variant', 'Cancel'],
				db='New Variant',
				cb='Cancel',
				ds='Cancel'
				)

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

			# New variant means we need to increment the variable and save the scene
			elif query == 'New Variant':
				self.variant = next_variant
				self._updateOut()
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
		''' Checks whether a passed path/folder exists and has a project definition. 
			Returns: Tuple ((0, None): Doesn't exist, 
						    (1, None): Folder exists but no variations (files) exist,
						    (1, Float): Exists and has variations .. next available iteration is the tuple[1] '''
		folder_exists = os.path.exists(self.project_folder)
		scene_exists = os.path.exists(self.full_path)

		# If the project folder doesnt exist, just escape out immediately
		if not folder_exists:
			return (False, None)

		elif folder_exists and not scene_exists:
			self._makeProject()
			return (True, None)

		elif scene_exists:
			available_variation = self._incrVariant(version_only=True)
			return (True, available_variation)

	def _incrVariant(self, variant, version_only=False):
		''' This function recursively increments scene variant #'s attempting to find the first available 
			file name not already taken.

			Note that this function, while similar, works slightly differently from _incrVersion() in that
			it does not directly change values, merely checks.  Actual changing of values is handled
			after user confirmation in _initScene().'''
		file_name = self.maya_project_folder + 'scenes\\' + self.project_name + '_' + self._formatVariant(2) + '.mb'
		
		# We're working with a copy of the original value, not an object reference
		variant = self.variant
		if os.path.exists(file_name):
			variant += 1
			file_name = _incrVariant(variant, version_only)
		if version_only:
			return variant
		else: 
			return file_name

	def _incrVersion(self, version_only=False):
		''' This function recursively increments versions attempting to find the next available file name for a
			backup of the scene file. 

			Note that unlike _incrVariant(), this function will always change values in the SceneControl object,
			if it determines that the currently queued backup has already been saved.'''
		file_name = self.backup_folder + self.scene_name + '_' + self._formatVersion(4) + '.mb'

		if os.path.exists(file_name):
			self.version += 1
			file_name = _incrVersion()
		
		if version_only:
			return self.version
		else:
			self.backup_path = file_name 
			return file_name

	def _formatVariant(self, padding):
		return str(int(self.variant)).zfill(padding)
	def _formatVersion(self, padding):
		return str(int(self.version)).zfill(padding)

	def _updateOut(self):
		''' Updates the maya sceneControlObject with any internal changes made to the python SceneManager.'''
		self.scene_name = self.project_name +'_'+ _formatVariant(2)
		self.scene_controller.attr('Version').set(self.version)
		self.scene_controller.attr('Variation').set(self.variant)
		self.scene_controller.attr('SceneName').set(self.scene_name)
		self.scene_controller.attr('Deliverable').set(self.project_name)

	def _updateIn(self):
		''' Updates the python SceneControl object with any changes made to the sceneControlObject (such as 
			when a new scene is opened.) '''
		# Getting attrs from sceneControlObject
		self.scene_name   = self.scene_controller.attr('SceneName').get()
		self.project_name = self.scene_controller.attr('Deliverable').get()
		self.version      = self.scene_controller.attr('Version').get()
		self.variant      = self.scene_controller.attr('Variant').get()
		# Combining project name and variant to create a scene name
		self.scene_name = self.project_name +'_'+ _formatVariant(2)

		# Setting new values (i.e. doing the business)
		self.project_folder      = self.base_path + self.project_name
		self.maya_project_folder = self.project_folder + 'maya\\'
		self.backup_folder       = self.maya_project_folder + 'backup\\'
		self.full_path           = self.maya_project_folder + 'scenes\\' + self.scene_name + '.mb'
		self.backup_path         = self._incrVersion()

		return True

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
			if v:
				this_folder = this_folder + v
				print this_folder
				os.mkdir(this_folder)
		return True

	def save(self, *a):
		''' Saves a backup of the current scene and overwrites it as a master scene file. '''
		if not self.scene_controller:
			pm.warning('Can\'t use this command until you\'ve set up the scene in the pipeline.')

		# Save the backup
		self.backup_path = self._incrVersion()
		try:
			pm.file(rename=self.backup_path)
			pm.file(save=True, type='mayaBinary')
		except:
			pm.warning('Failed to save backup!!  Check your scene file name and save an emergency local backup.')
		# Save the master
		try:
			pm.file(rename=self.full_path)
			pm.file(save=True, type='mayaBinary')
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

	@classmethod
	def open(self, *a):
		''' Opens a scene browsing UI and sets the associated project. '''
		new_file = pm.fileDialog2(fm=1, ds=1, dir=self.base_path)
		if not new_file:
			return None
		try:
			pm.file(new_file, open=True)
		except:
			pm.warning('Could not open file: ' + new_file)

		try:
			self._updateIn()

	@classmethod
	def submit(self, *a):
		''' Submits the current scene to the render farm. '''
		sub = submit.RenderSubmitWindow()
		return True

try:
	pm.lockNode(pm.PyNode('sceneControlObject'), lock=False)
	pm.delete(pm.PyNode('sceneControlObject'))
except: pass
import pipeline.cfb as cfb
test = SceneManager(cfb.ANIMATION_PROJECT_DIR, cfb.FOLDER_STRUCTURE)