import pymel.core as pm
import re
import yaml

# internal modules
import pipeline.vray.aov as aov

class Layer( object ):
    """Layer is an object used by the sort controller to parse information about a layer currently
    under control by the script.  This object contains the following attributes:
    - type: the type of layer (beauty, utility)
    - depth: the bit depth of the layer (16 or 32-bit)
    - bty_obj / mat_obj / pvo_obj / del_obj: lists the geometry in the layer (in the form of sg_groups) 
        and the attribute names indicate how they are flagged for visibility.
    - lights: the lights in the layer (lg_groups)


    It must be instantiated with a key/value pair, with the key being the name of the layer and the value
    being a valid sort controller dictionary (using the formatting from sorting.yaml)"""

    def __init__(self, name, dictionary):
        # The name of the render layer
        self.name = name

        # The type of render layer (beauty/utility)
        self.type = dictionary['type']

        # The bit depth of the layer, based on type
        if self.type != 'utility':
            self.depth = 16
        elif self.type == 'utility':
            self.depth = 32

        # Each of these contains a list of sg_groups in the scene, and decides how their visibilty is
        # flagged to the renderer.  Beauty, aov-only, primary visibility, occlusion (black holed)     
        try: self.bty_obj = dictionary['rgba']
        except: self.bty_obj = None

        try: self.aov_obj = dictionary['aov']
        except: self.aov_obj = None

        try: self.pvo_obj = dictionary['pv_off']
        except: self.pvo_obj = None

        try: self.occ_obj = dictionary['occlude']
        except: self.occ_obj = None

        # The lg_groups (lights) which should be added to the layer
        try: self.lights = dictionary['lights']
        except: self.lights = None

    def __repr__(self):
        return str(self.name)



class SortControl( object ):
    """SortControl is a custom data structure intended for assisting the building of render layers,
    render settings and framebuffers for a given element in a scene.  For example, the main logo, the 
    environment, a particular character, or any category of object requiring sorting into separate
    render layers with different visibility flags on each one."""

    def __init__(self, database, element, framebuffers):
        """'Element' is the type of object requesting a sort controller.  Potential keywords would be
        things like CFB_Logo, Team_Logo, Environment, etc.  See sorting.yaml's ELEMENT: attribute for the
        full list. """

        self.element = element
        self.framebuffers = framebuffers

        yaml_stream = open(database)
        stream = yaml.load_all(yaml_stream)


        #with open(cfb.SORTING_DATABASE) as yaml_stream:
        #    stream = yaml.load_all(yaml_stream)

        # Find the requested dictionary and close the yaml file
        for element_dictionary in stream:
            try:
                check = element_dictionary['ELEMENT']
            except:
                continue

            if check == element:
                break
            else:
                element_dictionary = None
                continue

        # If the loop breaks/ends with no match, it will remain None
        if element_dictionary == None:
            pm.error('No sorting dictionary found for element: ' + str(element) + '!')

        yaml_stream.close()

        # The name of this dictionary is no longer needed, so we delete it to make parsing easier.
        del element_dictionary['ELEMENT']

        # Create a list of Layer objects for parsing.  (See Layer class for description.)
        self.layers = []
        for k,v in element_dictionary.iteritems():
            layer = Layer(k,v)
            self.layers.append(layer)


    def __repr__(self):
        __repr = "\n" + str(self.element) + "\n" + str([str(l) for l in self.layers])
        return __repr


    def run(self):
        """ Sorts the objects under this controller into their designated layers, set their
        corresponding visibility flags, and enable the correct framebuffers."""
        for layer in self.layers:

            # Create the render layer, if it doesn't exist.
            makeLayer(layer.name)

            # Switch to that layer (for overriding purposes)
            pm.editRenderLayerGlobals(crl=layer.name)

            # Add the sg_groups (geometry) to the layer
            # Beauty objects
            if layer.bty_obj:
                for sg in layer.bty_obj: 
                    addToLayer( sg, layer.name )
                    setVisibility( sg, 'rgba')
            # Utility objects
            if layer.aov_obj:
                for sg in layer.aov_obj:
                    addToLayer( sg, layer.name )
                    setVisibility( sg, 'aov')
            # Primary visibility disabled objects
            if layer.pvo_obj:
                for sg in layer.pvo_obj:
                    addToLayer( sg, layer.name )
                    setVisibility( sg, 'pv_off')
            # Occlusion objects
            if layer.occ_obj:
                for sg in layer.occ_obj:
                    addToLayer( sg, layer.name )
                    setVisibility( sg, 'occlude')


            # Add the lg_groups (lights) to the layer
            if layer.lights:
                for lg in layer.lights:
                    addToLayer( lg, layer.name )

            # Enable framebuffers for the layer, based on type
            setFramebuffers( layer.type, self.framebuffers )
            # Set any hard-coded exceptions for this element in this layer
            exceptionCommands( self.element, layer.type )



#####################################
### LAYER ASSIGNMENT & OVERRIDING ###
#####################################


def addToLayer(  sort_set, layer, rm=False ):
    """ Assign the objects in a sortgroup to a render layer. """
    
    ## Since some scenes will have multiple sort sets with the same name, including
    ## a namespace, we will have to include logic to account for this
    # Search for all sortgroups matching the name passed to the function
    reg = re.compile(sort_set)
    if 'sg_all' in sort_set:
        all_matching = pm.ls(typ='VRayObjectProperties')
    elif 'lg_all' in sort_set:
        all_matching = pm.ls(typ='VRayRenderElementSet')
    elif 'sg_' in sort_set:
        all_matching = pm.ls(regex=reg, typ='VRayObjectProperties')
    elif 'lg_' in sort_set:
        all_matching = pm.ls(regex=reg, typ='VRayRenderElementSet')
        
    # Loop through all the matching sets and add them to their assigned layer
    for sort_set in all_matching:
        try:
            # The nodes / sorting set members that will be assigned to the render layer.
            nodes = sort_set.inputs()         
            if rm: # Remove flag is true
                [pm.editRenderLayerMembers( layer, n, r=True ) for n in nodes]
            else: # Remove flag is false (aka add)
                [pm.editRenderLayerMembers( layer, n ) for n in nodes]
        except:
            pm.warning ('Could not add ' + sort_set + ' to ' + layer + '.')
        
        # Not so much a warning as an echo.
        print ('SORTING REPORT :: Successfully added ' + sort_set + ' to ' + layer + '.')


def setVisibility( sort_set, override ):
    """ Enables the visibility state overrides on sortgroups based on keyword inputs. """

    # Ignore light and displacement groups
    if 'lg_' in sort_set or 'dg_' in sort_set:
        return None

    ## Since some scenes will have multiple sort sets with the same name, including
    ## a namespace, we will have to include logic to account for this
    reg = re.compile(sort_set)
    all_matching = pm.ls(regex=reg)
    
    if all_matching == []:
        return None

    # Loop through all matching sort sets, enable RL override on the relevant attrs,
    # and set the flags for each type of visibility.
    for sort_set in all_matching:

        enableOverride( sort_set.attr('primaryVisibility') )
        enableOverride( sort_set.attr('matteSurface') )
        enableOverride( sort_set.attr('alphaContribution') )
        enableOverride( sort_set.attr('generateRenderElements') )

        if override == 'rgba':
            sort_set.matteSurface.set(0)
            sort_set.alphaContribution.set(1)
            sort_set.primaryVisibility.set(1)
            sort_set.generateRenderElements.set(1)        
        elif override == 'occlude':
            sort_set.matteSurface.set(1)
            sort_set.alphaContribution.set(-1)
            sort_set.primaryVisibility.set(1)
            sort_set.generateRenderElements.set(0)
        elif override == 'pv_off':
            sort_set.matteSurface.set(0)
            sort_set.alphaContribution.set(0)
            sort_set.primaryVisibility.set(0)
            sort_set.generateRenderElements.set(0)
        elif override == 'aov':
            sort_set.matteSurface.set(1)
            sort_set.alphaContribution.set(1)
            sort_set.primaryVisibility.set(1)
            sort_set.generateRenderElements.set(1)        
        return True


def setFramebuffers( layer_type, framebuffers ):
    """ Enables the passes specified in the sort module global variables. """
    try:
        layer_buffers = framebuffers[layer_type]
    except:
        pm.warning('Error retrieving layer type from framebuffers list.')
        return False

    # First step: check that all existing framebuffers are turned off (as a layer override)
    existing = pm.ls(typ='VRayRenderElement')
    if existing:
        for fb in existing:
            enableOverride(fb.enabled)
            fb.enabled.set(0)
    
    # Lighting component framebuffers (beauty passes)
    if layer_type != 'utility':
        for fb in layer_buffers:
            print 'Enabling buffer: ' + str(fb)
            fb = aov.makeLightComponentBuffer(fb)
            enableOverride(fb.enabled)
            fb.enabled.set(1)

    # AOV / data framebuffers (utility passes)
    elif layer_type == 'utility':
        for fb in layer_buffers:
            print 'Enabling buffer: ' + str(fb)
            fb = aov.makeUtilityBuffer(fb)
            enableOverride(fb.enabled)
            fb.enabled.set(1)


def setExceptions( element_name, layer_type=None, layer_name=None ):
    ''' All the 
    if element_name == 'CFB_Logo' and layer_type == 'beauty':
        with pm.PyNode('FRONT_GLASS_BLENDMTL') as shader:
            fb = makeExTex('clearCoat', shader.outColor)
        with pm.PyNode('CARBON_FIBER_BLENDMTL') as shader:
            fb = makeExTex('carbonFiber', shader.outColor)
        return


# Helper Functions

def getAllSortgroups( sg=True, lg=False ):
    '''Return a list of all Light Select Sets and Object Properties Groups'''
    if sg and not lg:
        return pm.ls(type='VRayObjectProperties')
    elif lg and not sg:
        return pm.ls(type='VRayRenderElementSet')
    elif lg and sg:
        return pm.ls(type='VRayObjectProperties') + pm.ls(type='VRayRenderElementSet')


def makeLayer( name=None ):
    """ A Layer creation widget. """

    if not name:
        run = pm.promptDialog(
                title='Create New Layer',
                message='Enter Name:',
                button=['OK', 'Cancel'],
                defaultButton='OK',
                cancelButton='Cancel',
                dismissString='Cancel'
                )
        if run == 'OK':
            name = pm.promptDialog(query=True, text=True)
        else:
            return None
    try:
        exists = pm.PyNode(name)
        if exists:
            pm.warning('[ '+ name + ' ] Layer (or an object) with that name already exists.  Skipping...')
            return False
    except:
        lyr = pm.createRenderLayer( name=name, number=1, empty=True )
        return lyr
    

def getAllLayers():
    """ Returns a list of all render layers. """
    return [layer for layer in pm.ls(type='renderLayer') if not 'defaultRenderLayer' in str(layer)]


def enableOverride( attr ):
    ''' Enables the override of a specified attribute on the current render layer. '''
    enabled = pm.editRenderLayerAdjustment( query=True )

    if not enabled or not attr in enabled:
        pm.editRenderLayerAdjustment( attr )

    return True

def factory(*a):
    sorter = SortControl('Factory')
    sorter.run()