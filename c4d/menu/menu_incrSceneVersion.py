"""
Version Up Scene

Copyright: 2016 ESPN Productions
Compatible with Cinema4D R14, R15, R17
Author: Mark Rohrer (mark.rohrer@espn.com)

Name-US: Version Up Scene
Description-US: Increments the scene's version number by 1 (for render output.)
"""

import c4d
from c4d import gui

from pipeline.c4d import scene


def main():
	scn = scene.Scene()
	scn.versionUp()

if __name__ == '__main__':
	main()