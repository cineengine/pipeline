"""
Change Team Colors

Copyright: 2016 ESPN Productions
Compatible with Cinema4D R14, R15, R17
Author: Mark Rohrer (mark.rohrer@espn.com)

Name-US: Change Team Colors
Description-US: For properly named materials, this will set their colors based on Tricode input.
"""

import c4d
from c4d import gui

from pipeline.c4d import scene


def main():
	dlg = scene.TeamColorWindow()
	dlg.Open(c4d.DLG_TYPE_MODAL, defaultw=300, defaulth=100)

if __name__ == '__main__':
	main()