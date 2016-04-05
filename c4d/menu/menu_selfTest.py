"""
Scripts Self-Test

Copyright: 2016 ESPN Productions
Compatible with Cinema4D R14, R15, R17
Author: Mark Rohrer (mark.rohrer@espn.com)

Name-US: Scripts Self-test
Description-US: Tests that all scripts are installed and working
"""

import c4d
from c4d import gui


def main():
	output = ''
	try:
		from pipeline.c4d import core
		output+='pipeline.c4d.core loaded!\n'
	except:
		output+='pipeline.c4d.core FAILED!\n'	

	try:
		from pipeline.c4d import scene
		output+='pipeline.c4d.scene loaded!\n'
	except:
		output+='pipeline.c4d.scene FAILED!\n'

	try:
		from pipeline.c4d import database
		output+='pipeline.c4d.database loaded!\n'
	except:
		output+='pipeline.c4d.database FAILED!\n'

	try:
		prod_list = database.getAllProductions()
		output+='Production database found!\nList of available productions:\n'
		for p in prod_list:
			output+='  {}\n'.format(p)
			try:
				team_list = database.getAllTeams(p)
				output += 'Found {} teams in database for {}\n'.format(len(team_list), p)
			except:
				output+= 'Team database not found for {}!\n'.format(p)
	except:
		output+='Production database not found!\n'


	widget = gui.MessageDialog(output)

if __name__ == '__main__':
	main()