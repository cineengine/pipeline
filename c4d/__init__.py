__docstring__  = "Backend utilities for ESPN's Cinema4D software pipeline. Intended for use with the ESPNPipelineMenu plug-in."
__author__     = "Mark Rohrer"
__copyright__  = "Copyright 2017, ESPN Productions"
__credits__    = ["Mark Rohrer", "Martin Weber"]
__license__    = "Educational use only, all rights reserved"
__version__    = "1.1"
__date__       = "2/16/17"
__maintainer__ = "Mark Rohrer"
__email__      = "mark.rohrer@espn.com"
__status__     = "Soft launch"

from pipeline.c4d import debug
debug.info("Loaded ESPN backend utilities for C4D", "Version {0}: {1}".format(__version__, __date__))