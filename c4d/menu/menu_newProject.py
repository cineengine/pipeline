"""
Create New Project

Copyright: 2016 ESPN Productions
Compatible with Cinema4D R14, R15, R17
Author: Mark Rohrer (mark.rohrer@espn.com)

Name-US: Create New Project
Description-US: Creates a new project, including folders, and saves the scene with a backup.
"""

import c4d
from pipeline.c4d import scene

def main():
	dlg = scene.ProjectInitWindow()
	dlg.Open(c4d.DLG_TYPE_MODAL, defaultw=300, defaulth=50)

if __name__ == '__main__':
	main()