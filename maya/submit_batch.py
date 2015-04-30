import os
import subprocess
import pymel.core as pm
import pprint

default_priority = '5000'

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
        
        #################################################################################
        ## UI LAYOUT
        #################################################################################

        main_layout = pm.formLayout(p=self)

        # input / output paths
        column = pm.columnLayout(p=main_layout, width=720)
        job_text = pm.textFieldGrp(
            'job_text',
            label='Job Name', 
            text=self.submit_dict['name'], 
            cc=self.setName, 
            tcc=self.setName,
            p=column,
            cw2=(110,655)
            )
        scene_text = pm.textFieldGrp(
            'scene_text',
            label='Scene File', 
            text=self.submit_dict['package']['scenefile'], 
            cc=self.setScenePath, 
            tcc=self.setScenePath,
            p=column,
            cw2=(110,655)
            )
        project_text = pm.textFieldGrp(
            'project_text',
            label='Project Path', 
            text=self.submit_dict['package']['-proj'],
            ed=False,
            p=column,
            cw2=(110,655)
            )
        outdir_text = pm.textFieldGrp(
            'outdir_text',
            label='Render Path (optional)', 
            text='',
            cc=self.setRenderPath,
            p=column,
            cw2=(110,655)
            )

        # 2 columns
        column = pm.rowLayout(p=main_layout, nc=2)
        rows = pm.columnLayout(width=200, p=column)
       
        # frame range
        frange_text = pm.textFieldGrp(
            'frange_text',
            l='Frame Range', 
            text=self.submit_dict['package']['range'], 
            cc=self.setRange,
            tcc=self.setRange,
            cw2=(110, 80), 
            p=rows
            )

        chunk_text = pm.textFieldGrp(
            'chunk_text',
            l='Chunk Size',
            text='5',
            cc=self.setChunk,
            tcc=self.setChunk,
            cw2=(110, 80),
            p=rows
            )

        # num. threads
        threads_col = pm.rowLayout(p=rows, nc=2)
        threads_text = pm.textFieldGrp(
            'threads_text',
            l='Num. Threads',
            text='16',
            tcc=self.setThreads,
            cw2=(110, 40),
            p=threads_col
            )

        threads_chkbox = pm.checkBox(
            'threads_chkbox',
            l='All',
            value=False,
            cc=self.setThreads,
            p=threads_col
            )

        # priority
        priority_text = pm.textFieldGrp(
            'priority_text',
            l='Priority', 
            text=default_priority, 
            cc=self.setPriority,
            tcc=self.setPriority,
            cw2=(110, 80),
            p=rows)

        # cluster
        cluster_col = pm.rowLayout(p=rows, nc=2)
        cluster_text = pm.textFieldGrp(
            'cluster_text',
            l='Cluster', 
            text='/',
            cc=self.setCluster,
            tcc=self.setCluster,
            cw2=(110, 40), 
            p=cluster_col
            )

        restrict_chkbox = pm.checkBox(
            'restrict_chkbox',
            l='Res.',
            value=False,
            cc=self.setCluster,
            p=cluster_col
            )

        restrict_text = pm.textFieldGrp(
            'restrict_text',
            l='Restrict to Clusters',
            text='',
            cc=self.setCluster,
            tcc=self.setCluster,
            cw2=(110, 80),
            enable=False,
            p=rows
            )

        buttons = pm.columnLayout(p=column)
        submit_single_btn = pm.button(label='Submit Current Layer', width=565, height=60, c=self.submit, p=buttons)
        submit_all_btn    = pm.button(label='Submit All Renderable Layers', width=565, height=60, c=self.submit_all, p=buttons)

        main_layout.redistribute()

    ### UI FUNCTIONS
    def setChunk(self, *a):
        new = pm.textFieldGrp('chunk_text', q=True, text=True)
        self.submit_dict['package']['rangeExecution'] = 'chunks:{}'.format(new)
        return

    def setCluster(self, *a):
        # query the checkbox
        box_checked  = pm.checkBox('restrict_chkbox', q=True, value=True)
        cluster      = pm.textFieldGrp('cluster_text', q=True, text=True)
        restrictions = pm.textFieldGrp('restrict_text', q=True, text=True)
        
        self.submit_dict['cluster'] = cluster

        if box_checked:
            pm.textFieldGrp('restrict_text', e=True, enable=True)
            self.submit_dict['restrictions'] = restrictions

        elif not box_checked:
            pm.textFieldGrp('restrict_text', e=True, enable=False)
            self.submit_dict['restrictions'] = ''
        return

    def setThreads(self, *a):
        # query the checkbox
        box_checked = pm.checkBox('threads_chkbox', q=True, value=True)

        # if checked, ignore the text box, set threads to all
        if box_checked:
            pm.textFieldGrp('threads_text', e=True, enable=False) 
            self.submit_dict['reservations'] = ('host.processors=1+')
            self.submit_dict['package']['renderThreads'] = 0
            self.submit_dict['requirements'] = 'host.processors.used==0'

        # if unchecked, query the text field
        if not box_checked:
            pm.textFieldGrp('threads_text', e=True, enable=True)
            threads = pm.textFieldGrp('threads_text', q=True, text=True)
            self.submit_dict['reservations'] = ('host.processors=' + str(threads))
            self.submit_dict['package']['renderThreads'] = int(threads)
            self.submit_dict['requirements'] = ''
        return

    def setName(self, *a):
        new = pm.textFieldGrp('job_text', q=True, text=True)
        self.submit_dict['name'] = new
        return

    def setPriority(self, *a):
        new = pm.textFieldGrp('priority_text', q=True, text=True)
        self.submit_dict['priority'] = new
        return

    def setScenePath(self, *a):
        new = pm.textFieldGrp('scene_text', q=True, text=True)
        self.submit_dict['package']['scenefile'] = new
        return

    def setRenderPath(self, *a):
        new = pm.textFieldGrp('outdir_text', q=True, text=True)
        self.submit_dict['package']['-rd'] = new
        pass

    def setRange(self, *a):
        new = pm.textFieldGrp('frange_text', q=True, text=True)
        self.submit_dict['package']['range'] = new
        return

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
        layer_name      = str(pm.editRenderLayerGlobals(q=True, crl=True))

        submit_dict = {'name': pm.sceneName().basename().rstrip('.mb'),
               'prototype':'cmdrange',
               'package':{'simpleCmdType': 'Maya BatchRender (vray)',
                          'scenefile':     toUNC(scene_file_path),
                          '-proj':         toUNC(project_path), 
                          'range':         frame_range,
                          '-rl':           layer_name,
                          'renderThreads': 16,
                          'mayaExe':       "R:\\Program Files\\Autodesk\\Maya2015\\bin\\Render.exe",
                          'rangeExecution': 'chunks:5'
                          },
                'cluster': '/',
                'restrictions': '',
                'requirements': '',
                'kind': '',
                'priority': str(5000),
                'cpus': str(183),
                'reservations': 'host.processors=16',
                'flagsstring': 'auto_wrangling,disable_windows_job_object'
              }

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

        return submit_dict


    def run(self):
        self.show()


    def submit( self, qube_gui=0, *a ):
        """ Runs the Qube submission console command for the current render layer. """

        layer = pm.editRenderLayerGlobals(q=True, crl=True)
        self.submit_dict['package']['-rl'] = str(layer)
        self.submit_dict['name'] = pm.sceneName().basename().rstrip('.mb') + ' : ' + str(layer)

        if qube_gui:
            subprocess.Popen(['c:\\program files (x86)\\pfx\\qube\\bin\\qube-console.exe', '--submitDict', str(self.submit_dict)])
        else:
            subprocess.Popen(['c:\\program files (x86)\\pfx\\qube\\bin\\qube-console.exe', '--nogui', '--submitDict', str(self.submit_dict)])

    def submit_all(self, *a):
        """ Iterates over all active render layers and submits each one individually. """

        render_layers = [layer for layer in pm.ls(type='renderLayer') if (not 'defaultRenderLayer' in str(layer)) and layer.renderable.get()]

        for layer in render_layers:
            pm.editRenderLayerGlobals(crl=layer)
            self.submit()


    def __test(self, *a):
        layer = pm.editRenderLayerGlobals(q=True, crl=True)
        self.submit_dict['package']['-rl'] = str(layer)
        self.submit_dict['name'] = pm.sceneName().basename().rstrip('.mb') + ' : ' + str(layer)

        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(self.submit_dict)
        return

def getSceneUserCameras( *a ):
    """Returns a list of all non-default cameras in the scene """
    default_cameras = ['topShape', 'sideShape', 'frontShape', 'perspShape']
    cams = [str(cam) for cam in pm.ls(typ='camera') if cam not in default_cameras and cam.renderable.get()]
    if len(cams) > 0:
        return cams
    else: return None


def toUNC( path ):
    """ Force updates drive mapping to unc paths """
    path = path.replace('\\','/')
    return str(path.replace('Y:/','//cagenas/'))


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

def run(*a):
    submission = RenderSubmitWindow()
    submission.run()
    return
