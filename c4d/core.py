import c4d
import re


def ls( obj_=None, type_=c4d.BaseObject ):
	''' Returns a list of objects of specified type (default is BaseObject) that are either 
	    currently selected, or passed by object reference. Both types are validated before 
	    being returned as a list.

		Feature request: List objects by name using regex '''
	# Get selection if no object reference is passed
	if not (obj_):
		obj_ = c4d.documents.GetActiveDocument().GetSelection()


	elif (isinstance(obj_, str)):
		obj_ = c4d.documents.GetActiveDocument().SearchObject(obj_)


	# If a passed object is not already a list, we force the recast
	if not (isinstance(obj_, list)):
		obj_ = [obj_]

	
	# Cull any selected elements that don't match the specified object type
	for o in obj_:
		if not (isinstance(o, type_)):
			obj_.remove(o)
		else: continue


	if obj_ == []:
		obj_ = None

	# Returns a list of the specified object type
	return obj_

