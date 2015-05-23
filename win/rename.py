# !/usr/bin/python

import os, sys
import time

# Path to the team directory
BASE_PATH = "//cagenas/Workspace/MASTER_PROJECTS/CFB_15/PROJECTS/000_Animation/CFP_E_TEXT_TRANS/render_2d/TEAM/"

def renameFrame( tricode, padding, split_char ):

    base_dir = os.listdir(BASE_PATH)
    team_path = os.path.join(BASE_PATH, tricode)                    # BASE_PATH/AFA
    
    if os.path.isdir(team_path):
        team_dir = os.listdir(team_path)
        for term_folder in team_dir:                                # BASE_PATH/AFA/1st_Down
            print term_folder
            term_path = os.path.join(team_path, term_folder)
            if os.path.isdir(term_path):
                for f in os.listdir(term_path):                     # BASE_PATH/AFA/1st_Down/1st_Down.01.png
                    # Take out the term_folder
                    frame_num = f.replace(term_folder, "")
                    # Take out the split character
                    if (frame_num[0] == '_' or frame_num[0] == '.'):
                        frame_num = frame_num[1:]
                    # Format the frame number
                    frame_num_split = frame_num.split(".")
                    #if len(frame_num_split) < 3:
                    #    continue
                    frame_num_strip = frame_num_split[0].lstrip('0')
                    frame_num = frame_num_strip.zfill(padding)
                    # Put it all back together with desired split character
                    new_filename = term_folder + split_char + frame_num + "." + frame_num_split[1]
                    try:
                        os.rename(os.path.join(term_path, f), os.path.join(term_path, new_filename))
                        time.sleep(.05)
                    except:
                        pass
tricode_input = sys.argv[1]
padding_input = int(sys.argv[2])
split_char_input = sys.argv[3]
renameFrame(tricode_input, padding_input, split_char_input)
