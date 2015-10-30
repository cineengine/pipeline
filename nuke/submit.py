from os import listdir, getcwd
from os.path import isfile, join, basename, isdir
import subprocess
import time
import sys

#WRITE_NODE_NAME = "WriteScenes"
#frame_range = "1-300"
cpus = 8

#cmdline version
def generatePackage(job_name, script, frange, priority, cpus, write_node=''):
    submit_dict = {
        'prototype'    : 'cmdrange',
        'name'         : job_name,
        'priority'     : str(priority),
        'cpus'         : '95',
        'groups'       : 'Nuke',
        'reservations' : 'host.processors={}'.format(cpus),
        'package'      : {
            'simpleCmdType'    : 'Nuke (cmdline)',
            'executable'       : "R:\\Program Files\\Nuke8.0v6\\nuke8.0.exe",
            'script'           : str(script),
            'executeNodes'     : write_node,
            'range'            : frange,
            '-m'               : str(cpus),
            'minOpenSlots'     : cpus,
            'renderThreadCount': cpus
            }
           
        }

    return submit_dict

# pyNuke version

def generatePackagePY(job_name, script, frange, priority, cpus, write_node=''):
    submit_dict = {
        'prototype': 'pyNuke',
        'name'     : job_name,
        'priority' : str(priority),
        'cpus'     : '95',
        'specificThreadCount': str(cpus),
        'groups'   : 'Nuke',
        'cluster'  : '/C',
        'restrictions': '/C',
        'package'  : {
            'pyExecutable' : "R:\\Program Files\\Nuke8.0v6\\nuke8.0.exe",
            'scriptPath'   : script,
            'executeNodes' : write_node,
            'range'        : frange
            }
        }

    return submit_dict


def singleNode(job_name, script, frange, priority, cpus, write_node):
    submit_dict = generatePackagePY(job_name, script, frange, priority, cpus, write_node)
    subprocess.Popen(['c:\\program files (x86)\\pfx\\qube\\bin\\qube-console.exe', '--nogui', '--submitDict', str(submit_dict)])
    time.sleep(3)


def folder(frame_range, write_node, nuke_file_path=None, prog_minmax=None, *a):
    if not nuke_file_path:
        nuke_file_path = raw_input('Enter the folder to parse: ')
    #start_frame = raw_input('Enter start frame: ')
    #end_frame = raw_input('Enter end frame: ')
    #frame_range = str(start_frame +"-"+ end_frame)

    nuke_files = [ (nuke_file_path + '\\' + f) for f in listdir(nuke_file_path) if isfile(join(nuke_file_path,f)) and ".nk" in f and not ".nk~" in f]
    #nk = nuke_files[0]
    progress_max = len(nuke_files)

    for i in range(progress_max):
        print "\n\n"
        print "SUBMITTING JOB ::: " + str(i+1) + " of " + str(progress_max+1)
        if prog_minmax:
            print "FROM FOLDER    ::: " + str(prog_minmax[0]+1) + " of " + str(prog_minmax[1]+1)
        print "\n\n"
        package = generatePackagePY(str(basename(nuke_files[i])), nuke_files[i], frame_range, 9999, cpus, write_node)
        subprocess.Popen(['c:\\program files (x86)\\pfx\\qube\\bin\\qube-console.exe', '--nogui', '--submitDict', str(package)])
        time.sleep(3)


def allFolders(base_folder=None, *a):
    if not folder:
        return None

    all_folders = [d for d in listdir(base_folder) if isdir(base_folder + d)]
    #progress_max = len(all_folders)
    progress_max = 4
    for i in range(progress_max):
        #print all_folders[i]
        prog = (i, progress_max)
        folder((base_folder + all_folders[i]), prog)


if __name__ == '__main__':
    frame_range = sys.argv[1]
    write_node = sys.argv[2]
    folder(frame_range, write_node, getcwd())
