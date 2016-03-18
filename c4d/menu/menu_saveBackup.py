"""
Save With Backup

Copyright: 2016 ESPN Productions
Compatible with Cinema4D R14, R15, R17
Author: Mark Rohrer (mark.rohrer@espn.com)

Name-US: Save With Backup
Description-US: Saves the current scene, and saves a copy in the backup folder as well.
"""

import c4d
from pipeline.c4d import scene

def main():
	scene_data = scene.getSceneData()
	scene.saveWithBackup(scene_data)

if __name__ == '__main__':
	main()