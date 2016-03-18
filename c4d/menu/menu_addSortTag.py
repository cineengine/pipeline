"""
Add Sorting Tag to Selection

Copyright: 2016 ESPN Productions
Compatible with Cinema4D R14, R15, R17
Author: Mark Rohrer (mark.rohrer@espn.com)

Name-US: Add Sorting Tag to Selection
Description-US: Adds a sorting tag to the current selection.  You will be prompted to name it.
"""

import c4d
from c4d import gui
from pipeline.c4d import core

def main():
	sel  = core.ls()
	if not (sel):
		return
	name = gui.RenameDialog('tag_name')
	if (name):
		for obj in sel:
			tag = core.tag(obj, c4d.Tannotation, name)[0]
			core.visibility(tag, v=0)

if __name__ == '__main__':
	main()