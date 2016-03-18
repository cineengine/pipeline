"""
Default Render Settings

Copyright: 2016 ESPN Productions
Compatible with Cinema4D R14, R15, R17
Author: Mark Rohrer (mark.rohrer@espn.com)

Name-US: Default Render Settings
Description-US: Restores the default render settings to the scene.
"""

import c4d
from pipeline.c4d import scene

def main():
	scene.setOutput()

if __name__ == '__main__':
	main()