from c4d import gui

SCENE_NEW     = 0
SCENE_OK      = 1
SCENE_BROKEN  = 2
SCENE_MISSING = 3

class BaseError(Exception):
    def __init__(self, message, alert=True):
        super(BaseError, self).__init__(message)
        self.message = message
        if (alert): self._alert()

    def _alert(self):
        notification = {
            0: 'Basic Error.  You should not be seeing this.'
        }
        gui.MessageDialog(notification[self.message])


class FileError(BaseError):
    def _alert(self):
        notification = {
            0: 'Scene backup folder not found or could not be created.',
            1: '',
            2: 'Your scene file name is invalid.  Must be name.#.c4d or name.c4d',
            3: 'Could not create one or more project folders.'
        }
        gui.MessageDialog(notification[self.message])


class PipelineError(BaseError):
    def _alert(self):
        notification = {
            0: 'No valid __SCENE__ object found. Has this scene been set up in the pipeline? If not, run the pipeline setup and try again.',
            1: 'Multiple __SCENE__ objects were found. Delete any extras from merged scenes to continue.',
            2: 'Existing __SCENE__ object found.  This command is intended to be run on a clean scene.',
            3: 'Could not load project data from database.  Is this scene saved on the network in a project folder?'
        }
        gui.MessageDialog(notification[self.message])


class DatabaseError(BaseError):
    def _alert(self):
        notification = {
            0: 'Master project database not found.',
            1: 'Production not found in database.',
            2: 'Team not found in production database.'
        }
