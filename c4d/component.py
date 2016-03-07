import c4d




def makeTag( obj_=None, type_=None, name=None ):
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