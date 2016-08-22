import json
import os.path

DELIVERABLE = "NBA_E_REG_TEAM_ENDSTAMP_01"

deliverable_folder = ["Y:/Workspace/MASTER_PROJECTS/NBA_2016/001_PROJECTS/000_Animation/{}/render_2d".format(DELIVERABLE), "", ""]
team_list = []

with open("Y:\\Workspace\\SCRIPTS\\pipeline\\database\\teams_nba.json", 'r') as stream:
    db = json.load(stream)

for k in db:
    team_list.append(k)

for team in sorted(team_list):
	deliverable_folder[1] = team
	deliverable_folder[2] = "{}_{}.#.png".format(DELIVERABLE, team)

	if not os.path.isdir(deliverable_folder[0] + '/' + deliverable_folder[1]):
		os.mkdir(deliverable_folder[0] + '/' + deliverable_folder[1])

    wn = nuke.nodes.Write(name='{}_wn'.format(team))
    wn.knob('file').setValue('/'.join(deliverable_folder))
    wn.knob('channels').setValue('rgba')
    wn.knob('file_type').setValue('png')