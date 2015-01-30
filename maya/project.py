# Built-in modules
import os

# Maya-specific modules
import pymel.core as pm
import pymel.core.system as pmsys

# ESPN-specific modules
import pipeline.maya.asset as asset


class SceneManager(object):
	def __init__(self, animation_base_dir, folder_structure):
		# The name of the project.  Ex: "CFB_S_GAMEDAY_REJOIN"
		self.project_name = ''
		# The name of the scene (including variation).  Ex: "CFB_S_GAMEDAY_REJOIN_01"
		self.scene_name = ''	
		# The project path of the scene file.  Ex: "V:\CFB_S_GAMEDAY_REJOIN\maya\"
		self.project_path = ''
		# The full path of the scene file.  Ex: "V:\CFB_S_GAMEDAY_REJOIN\maya\scenes\CFB_S_GAMEDAY_REJOIN_01.mb"
		self.full_path = ''
		# The full path of the next backup of this scene file.  Ex: "V:\CFB_S_GAMEDAY_REJOIN\maya\scenes\backup\CFB_S_GAMEDAY_REJOIN_01_v0002.mb"
		self.backup_path = ''
		# The base path for all projects
		self.base_path = animation_base_dir
		# Dictionary for this project's folder structure.  Found in pipeline.<project_name> module.
		self.folder_structure = folder_structure

		try:
			self.scene_controller = pm.PyNode('sceneControlObject')
			self._loadSceneData()

		except pm.MayaNodeError:
			success = self._initScene()
			if not success:
				pm.warning('Scene failed to initialize. Ask Mark.')

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
			self.scene_name = self.project_name + '_' + self._formatVariant(2)
			self.project_path = self.base_path + self.project_name + '\\maya\\'
			self.full_path = self.project_path + self.scene_name + '.mb'
			self._update()

		# Check if the project exists, and if any scene files exist (and if so, get the next available variant)
		exists, next_variant = self._isProject()

		# Nothing exists, make everything and save
		if not exists:
			try:
				print self.project_path
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

		# The project exists but there's nothing saved, so just save
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
				self._update()
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
		folder_exists = os.path.exists(self.project_path)
		scene_exists = os.path.exists(self.full_path)

		# If the project folder doesnt exist, just escape out immediately
		if not folder_exists:
			return (False, None)

		elif folder_exists and not scene_exists:
			self._makeProject()
			return (True, None)

		elif scene_exists:
			available_variation = self._incrVersion(self.project_path, self.project_name, self.variant, 2, version_only=True)
			return (True, available_variation)

	def _incrVersion(self, path, name, version, fill, version_only=False):
		''' Given a path, a file name, and a starting version number, this function recursively
			increments versions attempting to find the first available file name not already taken. '''
		file_name = path + name + '_' + self._formatVariant(2) + '.mb'
		if os.path.exists(file_name):
			version += 1
			file_name = _incrVersion(path, name, version, fill)
		
		if version_only:
			return version
		else: 
			return file_name

	def _formatVariant(self, padding):
		return str(int(self.variant)).zfill(padding)
	def _formatVersion(self, padding):
		return str(int(self.version)).zfill(padding)

	def _update(self):
		# Update the scene name with any changes to the variant
		#self.scene_name = self.scene_name[:2] + self._formatVariant(2)
		# Set current SceneManager attribute values on the maya placeholder object
		self.scene_controller.attr('Version').set(self.version)
		self.scene_controller.attr('Variation').set(self.variant)
		self.scene_controller.attr('SceneName').set(self.scene_name)
		self.scene_controller.attr('Deliverable').set(self.project_name)

	def _makeProject(self):
		''' Make a new workspace definition file (workspace.mel) for this scene, if needed. '''
		# First, check that it doesn't already exist
		if os.path.exists(self.project_path + '\\workspace.mel'):
			#print 'Loaded workspace.mel from ' + self.base_path + '\\maya\\'
			return True

		# open the default workspace template
		with open('\\\\cagenas\\workspace\\scripts\\maya\\workspace.mel', 'r') as workspace:
			workspace_lines = workspace.readlines()
		# modify the line for render output
		workspace_lines[56] = "workspace -fr \"images\" \"" + self.project_path.rstrip('maya\\').replace('\\','/') + "/render_3d\";\n"
		# and save it to the new project folder
		with open(self.project_path + 'workspace.mel', 'w') as workspace:
			workspace.writelines(workspace_lines)
		print 'Created workspace.mel for ' + self.project_path
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

	def _loadSceneData(self):
		self.name = pmsys.sceneName().basename().rstrip('.mb')
		pass

	def save(self, *a):
		''' Saves a backup of the current scene and overwrites it as a master scene file. '''

		pass

	def setProject(self, *a):
		''' Sets the current workspace to the specified path.'''
		try:
			pmsys.Workspace.open(self.project_path)
			print 'Set project to: ' + self.project_path
			return True
		except:
			pm.warning('Failed to set the specified project.  It probably doesn\'t exist')
			return False

	@classmethod
	def open(self, *a):
		''' Opens a scene browsing UI and sets the associated project. '''
		pass

	@classmethod
	def submit(self, *a):
		''' Submits the current scene to the render farm. '''
		pass
try:
	pm.lockNode(pm.PyNode('sceneControlObject'), lock=False)
	pm.delete(pm.PyNode('sceneControlObject'))
except: pass
import pipeline.cfb as cfb
test = SceneManager(cfb.ANIMATION_PROJECT_DIR, cfb.FOLDER_STRUCTURE)