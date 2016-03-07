import c4d
import os

def open( file_=None ):
	''' Open the specified project.  If no file is specified, open a dialog. '''
	if (file_):
		c4d.documents.LoadFile(file_)
	else:
		c4d.CallCommand(12095, 12095)


def setupScene():
	''' Init scene for pipeline stuff. '''



def setupFolders():
	''' Create project folders for this scene. '''
	return


def setupOutput():
	''' Set render output folders. '''
	return


def ls( obj_=None, type_=c4d.BaseObject ):
	''' Returns a list of objects of specified type (default is BaseObject) that are either 
	    currently selected, or passed by object reference. Both types are validated before 
	    being returned as a list.

		Feature request: List objects by name using regex '''
	# Get selection if no object reference is passed
	if not (obj_):
		obj_ = c4d.documents.GetActiveDocument().GetSelection()

	# If a passed object is not already a list, we force the recast
	elif not (isinstance(obj_, list)):
		obj_ = [obj_]

	# Cull any selected elements that don't match the specified object type
	for o in obj_:
		if not (isinstance(o, type_)):
			obj_.remove(o)
		else: continue

	# Returns a list of the specified object type
	return obj_


def createTag( obj_=None, type_=None, name=None ):
	''' Creates a tag on the selected (or specified) object. '''
	# Get the selected object, if none is passed
	obj_ = ls(obj_)
	# Empty return container
	tags = []
	# Make a tag for each object
	for o in obj_:
		tag = o.MakeTag(type_)
		# Add the tag to the return list
		tags.append(tag)
		# Name the tag
		if name:
			tag[c4d.ID_BASELIST_NAME] = name

	return tags


# Save scene file

# Import asset

# XRef asset

