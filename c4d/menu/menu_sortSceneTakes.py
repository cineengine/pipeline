"""
Sort Scene Takes

Copyright: 2016 ESPN Productions
Compatible with Cinema4D R14, R15, R17
Author: Mark Rohrer (mark.rohrer@espn.com)

Name-US: Sort Scene into Takes
Description-US: If the objects in the scene are tagged, this will sort them into their correct takes.
"""

import c4d
from pipeline.c4d import scene

def main():
	scene_data = scene.getSceneData()
	scene.sortTakes(scene_data)

if __name__ == '__main__':
	main()