# Production (object)
#
# A production represents a show or event package, and is the meta-container of many projects, deliverables,
# scene files, or elements all sharing an asset library, delivery specs, team of artists, or any combination
# of the above.
#
# Initialization:
# ->name:: (str) OPTIONAL -- search the database for the Production by name
# ->id:: (id) OPTIONAL -- search the database for the Production by id
# ->None:: (NULL) an empty, default production object, ready for creation
#
# Attributes:
# - id:: (hex) the database id of the production
# - name:: (str) the name of the production
# - folders:: (dict) the proto map of the folder structure for Projects belonging to this production
# - artists:: ([id]) a list of artists (as ids) assigned to this production
# - global_specs:: (Specs) global/default specs for the production
# - contact:: (id) placeholder
# - schedule:: (Schedule) placeholder
# - deliverables:: ([id]) a list of ALL deliverables attached to the production
# - projects:: ([id]) a list of ALL projects attached to the production
# - asset_library:: (id) The production's main asset library
#
# Derived attributes (from GLOBAL_PARAMETERS):
# - path:: (str/path) location of the production on the NAS
# - publish_path:: (str/path) location of the production on PublishData


# AssetLibrary (object)
# 
# An asset library consists of a dictionary of asset locations on a server.
#
# Attributes:
# [id]: (Asset)

# Asset:
# 
# An asset is a metadata container about a file object of some kind.
#
# Attributes:
# - name:: (str) name of the asset
# - path:: (str/path) location of the asset relative to main asset folder
# - type:: (str) file type of the asset
# - tags:: ([str]) list of searchable tags for the asset
# - production:: (id) production the asset belongs to (if applicable)


# Schedule (object)
#
# A table of deadlines and assignments pointing to database ids


# Specs (object)
#
# Specs is a container of globally-readable technical delivery specs for a project, deliverable, or scene.
#
# Initialization:
# ->production:: (id) populates the Specs of the passed production
# ->project:: (id) populates the Specs of the passed project (as delta compression)
#
# Attributes:
# - id:: (hex) the database id of the parameter set
# - name:: (str) colloquial name for the parameter set (ex. "720@60 / 32-bit RGBA")
# - xres:: (int)
# - yres:: (int)
# - frate:: (float)
# - bit_depth:: (int)
# - keyable:: (bool)
#
# Modified (platform-specific) attributes:
# - renderer:: (**id/str) the rendering engine used
# - render_settings:: (**dict) raytracing / global render settings
#
# Methods:
# (The Specs prototype will be modified based on API in their respective core sub-modules)
# - translate:: translates the generic Specs dictionary into a platform-specific object, modifying the syntax
#	as necessary or providing direct API calls to these parameters if available


# Project (object)
#
# A project object consists of core data about an animation project (one main conceptual-level scene, which may
# consist of many files or different versions of that scene.) 
#
# Initialization:
# ->project:: (id) OPTIONAL -- instances the object with pre-loaded information about an existing project
# ->production:: (id) OPTIONAL -- instances the object with pre-loaded information about a production
# ->name:: (str) OPTIONAL -- if passed with a production id, this will create a new project upon instancing
#
# Attributes:
# - id:: (hex) the database id of the project
# - production:: (id) the production database entry stores the location on the server and internal 
#   folder structure, as well as some of its core specs. since these are inherently dynamic attributes,
#   all of this data is derived at runtime, and so only the ID of the production is stored.
# - name:: (str) plaintext name of the project -- the foundation for all internal naming conventions
# - deadline:: (str) yep
# - specs:: ({delta} of this.production_global_specs) framerate, resolution, etc.  
#   anything that needs to remain flexible below the  production-level, i.e. things that may change 
#   based on delivery vector or creative need
# - artist:: (id) the lead artist responsible for the project
# - deliverables:: ([id]) a list of deliverables attached to the project
# - description:: (str) a plaintext description of the project
#
# Derived attributes: ->(production id)
# - path:: (str/path) location of the project folder on the server
# - render_output_paths:: (dict) location of the project's render folders on the server
# - production_global_specs:: (dict) the global production specs, which contributes to and is the generator
# 	for this.specs
#
# Methods:
# - get:: (proto modified by sub-modules) gets the project data of the active scene
# - set:: ->(id) (proto modified by sub-modules) sets / conforms the active scene into an existing project
# - create:: ->(id, str) creates a new project, including folders and database entries
# - archive:: archives a project into a backup folder, removing it from the active list
# - addDeliverable:: ->(str) adds a deliverable to the project
# - removeDeliverable:: --
# - changeArtist:: ->(id) changes the lead artist responsible for the element


# Deliverable (object)
#
# A deliverable belongs to a project, and represents a single quicktime that must be created.
# Some example deliverables for a project might be a sponsored, non-sponsored, INET, or team
# versions of the same core element.  This does NOT represent a "real" object, and is for tracking
# and database purposes only.
#
# Attributes:
# - id:: (hex) the database id of the deliverable
# - project:: (id) the parent project of the deliverable
# - name:: (str) the name of the deliverable, which consists of the project name with a suffix.
# - description:: (str) a plaintext description of the deliverable (optional)
# - artist:: (id)


# Scene (Project)
# Derived from a project object, a Scene is individual file belonging to that project, and might represent any discrete
# piece of a deliverable, be it a version, render pass, or some other miscellaneous pipelined scene file.
#
# Scene is the workhorse object within platform sub-modules, and as such is heavily modified to suit the
# needs of various apps.
#
# Initialization:
# ->app:: (id) OPTIONAL -- when instanced within a platform environment, this flag will modify
# 	the Scene methods to support various operations within that platform.
#
# Attributes:
# - id:: (hex) the database id of the scene
# - scene_name:: (str)
# - version:: (int)
# - artist:: (id)
#
# Derived attributes: ->(project id)
# - scene_path::
# - render_output_paths:: 
# - specs::
#
# Methods:
# - get:: (*id) (proto modified by sub-modules) if no id is passed, gets the scene data of the active scene
# - set:: ->(id) (proto modified by sub-modules) sets / conforms the active scene into an existing scene -- VERY DANGEROUS
# - create:: ->(id, str) creates a new scene within an existing project
# - archive:: archives a scene into the project's backup folder
# - changeArtist:: ->(id) changes the artist responsible for the scene.
# - render:: submits the scene to the render farm
# - setup:: sets the scene up for rendering
# - sort:: ->(id, **) sorts the scene for rendering
# - sanityCheck:: (flags) TD-level scene checking
# - build:: ->(id, **) builds a procedural scene based on some template
# - open:: ->(id) opens the scene with the passed id
# - save::
# - rename::
# - backup::



