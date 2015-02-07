Maya/Nuke/V-Ray Pipeline
Intended for private / collaborative use only.  It's fine if you borrow, just 
toss a link to my github page in your comments.

UPCOMING FEATURES
    - Maya UI widget            (maya/ui.py)
    - Scene opening & init      (maya/project.py)
    - Scene sorting on the fly  (maya/sort.py)
    - Scene sorting by database (maya/sort.py)
    - Equivalent versions for all functionality in Nuke

##############################################################################
CHANGELOG
##############################################################################
------------------------------------------------------------------------------
02/07/15

- The following modules are working and tested -- all command line at the moment
	- Sort controller       (maya/sort.py)
	- Project creation      (maya/project.py)
	- Scene saving & backup (maya/project.py) (open() currently doesn't work)
	- V-Ray framebuffers    (vray/renderElements.py)
	- V-Ray mattes          (vray/mattes.py) - note this is my OLD version
	- V-Ray set management  (vray/utils.py)
	- Teams database        (database/team.py)


- The following modules are due to be deprecated, once their useful code is
  copied into the correct modules & tested.
    - Old team module       (maya/team.py)
    - Build module          (maya/build.py)
    - Switch Team module    (maya/switchTeam.py) <-- this will be archived for
      championship purposes only

