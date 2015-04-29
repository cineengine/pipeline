import os
import subprocess
import pymel.core as pm

class RenderSubmitWindow(pm.uitypes.Window):

    def __init__(self):
        try:
            pm.deleteUI('qubeSubmitWindow')
        except: pass

        self.mw = 780
        self.setTitle('Submit Scene to Qube')
        self.setToolbox()
        self.setResizeToFitChildren(1)
        self.setSizeable(0)
        self.setWidth(self.mw)
        self.setHeight(250)

        self.submit_dict = self.gatherSceneData()

        self.base_job_name = self.submit_dict['name']

        #self.run()


    def __editDict(self, text_field, key_one, key_two=None):
        new_value = pm.textFieldGrp(text_field, q=True, text=True)

        if key_two:
            self.submit_dict[key_one][key_two] = new_value
        else:
            self.submit_dict[key_one] = new_value
        return True


    def __setThreads(self, text_field, chkbox_field):
        # query the checkbox
        box_checked = pm.checkBox(chkbox_field, q=True, value=True)

        # if checked, ignore the text box, set threads to all
        if box_checked:
            pm.textFieldGrp(text_field, e=True, enable=False) 
            self.submit_dict['reservations'] = ('host.processors=1+')
            self.submit_dict['package']['renderThreads'] = 0
            self.submit_dict['requirements'] = 'host.processors.used==0'

        # if unchecked, query the text field
        if not box_checked:
            pm.textFieldGrp(text_field, e=True, enable=True)
            threads = pm.textFieldGrp(text_field, q=True, text=True)
            self.submit_dict['reservations'] = ('host.processors=' + str(threads))
            self.submit_dict['package']['renderThreads'] = int(threads)
            self.submit_dict['requirements'] = ''

        return True


    def __setClusters(self, cluster_field, restrict_field, chkbox_field):
        # query the checkbox
        box_checked  = pm.checkBox(chkbox_field, q=True, value=True)
        cluster      = pm.textFieldGrp(cluster_field, q=True, text=True)
        restrictions = pm.textFieldGrp(restrict_field, q=True, text=True)
        
        self.submit_dict['cluster'] = cluster

        if box_checked:
            pm.textFieldGrp(restrict_field, e=True, enable=True)
            self.submit_dict['restrictions'] = restrictions

        elif not box_checked:
            pm.textFieldGrp(restrict_field, e=True, enable=False)
            self.submit_dict['restrictions'] = ''

        return True

    def __browse(self, text_field, folder=False):
        pass


    @classmethod
    def gatherSceneData( self, *a ):
        """Gathers scene information and executes the shell command to open a Qube submission window"""

        rg = pm.PyNode('defaultRenderGlobals')

        scene_file_path = pm.system.sceneName()
        project_path    = pm.workspace(q=True, rd=True).replace('/','\\')
        image_path      = os.path.join(project_path, pm.workspace('images', q=True, fre=True)).replace('/','\\')
        frame_range     = str(int(rg.startFrame.get())) + "-" + str(int(rg.endFrame.get()))
        scene_cameras   = getSceneUserCameras()
        renderer        = rg.ren.get()
        render_layers   = [layer for layer in pm.ls(type='renderLayer') if not 'defaultRenderLayer' in str(layer)]
        layer_name      = pm.editRenderLayerGlobals(q=True, crl=True)

        # SANITY CHECKS
        # 1- scene never saved
        if scene_file_path == '':
            pm.confirmDialog( title='Scene not saved.',
                              button='Whoops',
                              message='Please save scene on cagenas before submitting.',
                              defaultButton='Whoops'
                              )
            return 'sanity check fail'

        # 2- no user cameras in scene
        if scene_cameras == None:
            pm.confirmDialog( title='No renderable camera.',
                              button='Whoops',
                              message='No renderable cameras found in your scene.',
                              defaultButton='Whoops'
                              )
            return 'sanity check fail'

        elif len(scene_cameras) > 1:
            confirm = pm.confirmDialog( title='Multiple renderable cameras.',
                              button=('Whoops', 'That\'s fine'),
                              cancelButton='That\'s fine',
                              message='You have multiple renderable cameras in your scene.  All of them will be rendered.  Proceed?',
                              defaultButton='Whoops',
                              dismissString='That\'s fine'
                              )
            if confirm == 'That\'s fine':
                pass
            elif confirm == 'Whoops':
                return 'sanity check fail'

        # 3- animation rendering not enabled
        if rg.animation.get() == False:
            check = pm.confirmDialog( title='Animation not enabled.',
                                      button=('Whoops', 'That\'s fine'),
                                      cancelButton='That\'s fine',
                                      message='Animation is not enabled in your render globals.',
                                      defaultButton='Whoops',
                                      dismissString='That\'s fine'
                                      )
            print check
            if check == 'Whoops':
                return 'sanity check fail'
            else: pass

        # 4- framerate weirdness
        if (rg.endFrame.get() % int(rg.endFrame.get())):
            pm.confirmDialog( title='Framge range is strange!',
                              button='Whoops',
                              message='Animation frame range is wonky.  Did you change framerate?',
                              defaultButton='Whoops'
                              )
            return 'sanity check fail'        

        submit_dict = {'name': str( scene_file_path.basename().rstrip('.mb') ),
               'prototype':'cmdrange',
               'package':{'simpleCmdType': 'Maya BatchRender (vray)',
                          'scenefile':     str( toUNC(scene_file_path.replace('/','\\')) ),
                          '-proj':         str( toUNC(project_path) ), 
                          'range':         str( frame_range ), 
                          '-cam':          listToStr( scene_cameras ), 
                          '-rl':           str( layer_name ),
                          'renderThreads': 16,
                          'mayaExe':       'R:\\Program Files\\Autodesk\\Maya2015\\bin\\Render.exe',
                          '-rd':           toUNC(image_path)
                          },
                'cluster': '/',
                'restrictions': '',
                'renderThreads': 16,
                'requirements': '',
                'kind': '',
                'priority': str(5000),
                'cpus': str(183),
                'reservations': 'host.processors=16',
                'flagsstring': 'auto_wrangling,disable_windows_job_object'
              }              

        return submit_dict


    def run(self):
        main_layout = pm.formLayout(p=self)

        # input / output paths
        column = pm.columnLayout(p=main_layout, width=720)
        job_text = pm.textFieldGrp(
            label='Job Name', 
            text=self.submit_dict['name'], 
            cc=lambda *args: self.__editDict(job_text, 'name'), 
            tcc=lambda *args: self.__editDict(job_text, 'name'), 
            p=column,
            cw2=(110,655)
            )
        scene_text = pm.textFieldGrp(
            label='Scene File', 
            text=self.submit_dict['package']['scenefile'], 
            cc=lambda *args: self.__editDict(scene_text, 'package', 'scenefile'), 
            tcc=lambda *args: self.__editDict(scene_text, 'package', 'scenefile'),
            p=column,
            cw2=(110,655)
            )
        project_text = pm.textFieldGrp(
            label='Project Path', 
            text=self.submit_dict['package']['-proj'],
            ed=False,
            p=column,
            cw2=(110,655)
            )
        outdir_text = pm.textFieldGrp(
            label='Render Path (optional)', 
            text='',
            p=column,
            cw2=(110,655)
            )



        # 2 columns
        column = pm.rowLayout(p=main_layout, nc=2)
        rows = pm.columnLayout(width=200, p=column)
        # frame range
        frange_text = pm.textFieldGrp(
            l='Frame Range', 
            text=self.submit_dict['package']['range'], 
            cc=lambda *args: self.__editDict(frange_text, 'package', 'range'),
            tcc=lambda *args: self.__editDict(frange_text, 'package', 'range'),
            cw2=(110, 80), 
            p=rows
            )

        # num. threads
        threads_col = pm.rowLayout(p=rows, nc=2)
        threads_text = pm.textFieldGrp(
            l='Num. Threads',
            text='16',
            tcc=lambda *args: self.__setThreads(threads_text, threads_chkbox),
            cw2=(110, 40),
            p=threads_col
            )
        threads_chkbox = pm.checkBox(
            l='All',
            value=False,
            cc=lambda *args: self.__setThreads(threads_text, threads_chkbox),
            p=threads_col
            )

        # priority
        priority_text = pm.textFieldGrp(
            l='Priority', 
            text=self.submit_dict['priority'], 
            cc=lambda *args: self.__editDict(priority_text, 'priority'),
            tcc=lambda *args: self.__editDict(priority_text, 'priority'),
            cw2=(110, 80),
            p=rows)

        # cluster
        cluster_col = pm.rowLayout(p=rows, nc=2)
        cluster_text = pm.textFieldGrp(
            l='Cluster', 
            text=self.submit_dict['cluster'],
            cc=lambda *args: self.__setClusters(cluster_text, restrict_text, restrict_chkbox),
            tcc=lambda *args: self.__setClusters(cluster_text, restrict_text, restrict_chkbox),
            cw2=(110, 40), 
            p=cluster_col
            )
        restrict_chkbox = pm.checkBox(
            l='Res.',
            value=False,
            cc=lambda *args: self.__setClusters(cluster_text, restrict_text, restrict_chkbox),
            p=cluster_col
            )
        # num threads
        restrict_text = pm.textFieldGrp(
            l='Restrict to Clusters',
            text=self.submit_dict['restrictions'],
            cc=lambda *args: self.__setClusters(cluster_text, restrict_text, restrict_chkbox),
            tcc=lambda *args: self.__setClusters(cluster_text, restrict_text, restrict_chkbox),
            cw2=(110, 80),
            enable=False,
            p=rows
            )

        #submit_btn = pm.button(label='test', width=565, height=80, c=self.__test, p=column)
        buttons = pm.columnLayout(p=column)
        submit_single_btn = pm.button(label='Submit Current Layer', width=565, height=60, c=self.submit, p=buttons)
        submit_all_btn    = pm.button(label='Submit All Renderable Layers', width=565, height=60, c=self.submitAll, p=buttons)

        main_layout.redistribute()
        self.show()


    def submit( self, qube_gui=0, *a ):
        """ Runs the Qube submission console command for the current render layer. """

        layer = pm.editRenderLayerGlobals(q=True, crl=True)
        self.submit_dict['package']['layers'] = str(layer)
        self.submit_dict['name'] = self.base_job_name + ' : ' + str(layer)

        if qube_gui:
            subprocess.Popen(['c:\\program files (x86)\\pfx\\qube\\bin\\qube-console.exe', '--submitDict', str(self.submit_dict)])
        else:
            subprocess.Popen(['c:\\program files (x86)\\pfx\\qube\\bin\\qube-console.exe', '--nogui', '--submitDict', str(self.submit_dict)])


    def submitAll(self, *a):
        """ Iterates over all active render layers and submits each one individually. """

        render_layers = [layer for layer in pm.ls(type='renderLayer') if (not 'defaultRenderLayer' in str(layer)) and layer.renderable.get()]

        for layer in render_layers:
            pm.editRenderLayerGlobals(crl=layer)
            self.submit()


    def __test(self, *a):
        print self.submit_dict


def getSceneUserCameras( *a ):
    """Returns a list of all non-default cameras in the scene """
    default_cameras = ['topShape', 'sideShape', 'frontShape', 'perspShape']
    cams = [str(cam) for cam in pm.ls(typ='camera') if cam not in default_cameras and cam.renderable.get()]
    if len(cams) > 0:
        return cams
    else: return None


def toUNC( path ):
    """ Force updates drive mapping to unc paths """
    return path.replace('Y:\\','\\\\cagenas\\')

def listToStr( list_obj ):
    """ Converts a list of objects to a space-separated string of object names """

    if 'str' in str(list_obj.__class__):
        return list_obj
    elif not 'list' in str(list_obj.__class__):
        pm.error('Unexpected object type ' + str(list_obj.__class__) + ' in _listToStr.')
        return None

    out_str = ""

    for i in range(len(list_obj)):
        # if it is the only or last element in the list
        if (i+1) == len(list_obj):
            out_str += str(list_obj[i])
        # if it is the 1 to (n-1) element of the list
        elif (i+1) < len(list_obj):
            out_str = out_str + str(list_obj[i]) + " "        
        else: return '#EMPTY_LIST'
    return out_str

def submitJob( gui=True, *a ):
    """ Standalone function whihc runs the Qube submission console command for each renderable layer in the scene. """
    render_layers = [layer for layer in pm.ls(type='renderLayer') if (not 'defaultRenderLayer' in str(layer)) and layer.renderable.get()]

    for layer in render_layers:
        
        pm.editRenderLayerGlobals(crl=layer)
        submit_dict = RenderSubmitWindow.gatherSceneData()
        
        if submit_dict == 'sanity check fail':
            pm.warning("Failed sanity check :: there was a problem with your scene.")
            return None
        if gui:
            subprocess.Popen(['c:\\program files (x86)\\pfx\\qube\\bin\\qube-console.exe', '--submitDict', str(submit_dict)])
        else:
            subprocess.Popen(['c:\\program files (x86)\\pfx\\qube\\bin\\qube-console.exe', '--nogui', '--submitDict', str(submit_dict)])

def run(*a):
    submission = RenderSubmitWindow()
    submission.run()
    return
