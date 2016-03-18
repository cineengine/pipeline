"""
Create Take / Render Layer

Copyright: 2016 ESPN Productions
Compatible with Cinema4D R14, R15, R17
Author: Mark Rohrer (mark.rohrer@espn.com)

Name-US: Create Render Take (Layer)
Description-US: Creates a default render take / layer, with override groups.
"""

import c4d
from pipeline.c4d import core

def main():
	take = core.take('main', 1)

if __name__ == '__main__':
	main()