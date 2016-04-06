"""
Rename Scene

Copyright: 2016 ESPN Productions
Compatible with Cinema4D R14, R15, R17
Author: Mark Rohrer (mark.rohrer@espn.com)

Name-US: Rename Scene
Description-US: Renames a pipeline'd scene
"""

import c4d
from c4d import gui

from pipeline.c4d import scene


def main():
	scn = scene.Scene()
	scn.rename()

if __name__ == '__main__':
	main()