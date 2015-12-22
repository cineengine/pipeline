from maya import cmds

from maya import mel

from maya import OpenMayaUI as omui

from PySide.QtCore import * 

from PySide.QtGui import * 

from PySide.QtUiTools import *

from shiboken import wrapInstance 

import os.path







'''

espnMatteTagsUI.py



author:     Christopher Fung

contact:    christopher@mrfung.com

web:        http://www.mrfung.com



version:    0.3

date:       2015.03.13



Description:

    Designed to allow quick and compreshensive setting of tags on objects via vrayUserAttributes, 

    to later be converted into individual render elements for each tag allowing for easily identified

    and extractable mattes in composite.



    espnMatteTags



Notes:

  * Requires vrayformaya.mll to be activated (Obviously).



Limitations:

  * Very limited!



Updates:

  v0.3 Added "Append vrayUserAttributes" button



References:

  * http://knowledge.autodesk.com/search-result/caas/CloudHelp/cloudhelp/2015/ENU/Maya-SDK/files/GUID-3F96AF53-A47E-4351-A86A-396E7BFD6665-htm.html

  * http://danostrov.com/2012/10/27/creating-a-simple-ui-in-maya-using-pyqt/

  * https://github.com/throb/vfxpipe/blob/master/maya/vrayUtils/createTechPasses.py

  * http://stackoverflow.com/questions/3845423/remove-empty-strings-from-a-list-of-strings

    

'''







mayaMainWindowPtr = omui.MQtUtil.mainWindow() 

mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QWidget) 





class espnMatteTags(QWidget):

    def __init__(self, *args, **kwargs):

        super(espnMatteTags,self).__init__(*args, **kwargs)



        self.windowName = 'espnMatteTags'



        # Check to see if this UI is already open. If UI already exists, destroy it.

        if cmds.window(self.windowName, exists=True):

	    cmds.deleteUI(self.windowName)



        self.setParent(mayaMainWindow)

        self.setWindowFlags( Qt.Window )

        self.setObjectName(self.windowName)

        self.setWindowTitle(self.windowName)

        self.initUI()







    ####################################################################################################

    # Builds UI for espnMatteTags() functionality.        

    ####################################################################################################

    def initUI(self):



        ########################################################################

        #Create Widgets

        ######################################################################## 



        self.assetLabel = QLabel("Asset Tools", parent=self)

	self.tagsLE = QLineEdit('null', parent=self)

        self.addButton = QPushButton('Add vrayUserAttributes', self)

	self.addButton.clicked.connect(self.btnAddVrayUserAttributes) 

        self.getButton = QPushButton('Get vrayUserAttributes', self)

	self.getButton.clicked.connect(self.btnGetVrayUserAttributes) 

        self.setButton = QPushButton('Set vrayUserAttributes', self)

	self.setButton.clicked.connect(self.btnSetVrayUserAttributes)

        self.appendButton = QPushButton('Append vrayUserAttributes', self)

	self.appendButton.clicked.connect(self.btnAppendVrayUserAttributes)





        self.renderLabel = QLabel("Render Tools", parent=self)

        self.createButton = QPushButton('Create Render Elements', self)

	self.createButton.clicked.connect(self.btnCreateRenderElements) 

        self.destroyButton = QPushButton('Destroy Render Elements', self)

	self.destroyButton.clicked.connect(self.btnDestroyRenderElements) 



        self.debugLabel = QLabel("Debug", parent=self)

	self.verboseCB = QCheckBox('Verbose', parent=self)

        self.verboseCB.stateChanged.connect(self.cbVerboseMode)

	self.verboseCB.setChecked(True)



	########################################################################

        # Layout the widgets

        ########################################################################

	assetToolsLayout = QBoxLayout(QBoxLayout.LeftToRight)

        assetToolsLayout.addWidget(self.addButton)

        assetToolsLayout.addWidget(self.getButton)

        assetToolsLayout.addWidget(self.setButton)

        assetToolsLayout.addWidget(self.appendButton)



	renderToolsLayout = QBoxLayout(QBoxLayout.LeftToRight)

        renderToolsLayout.addWidget(self.createButton)

        renderToolsLayout.addWidget(self.destroyButton)



        self.layout = QBoxLayout(QBoxLayout.TopToBottom, self)

        self.layout.addWidget(self.assetLabel)

        self.layout.addWidget(self.tagsLE)

        self.layout.addLayout(assetToolsLayout)

        self.layout.addWidget(self.renderLabel)

        self.layout.addLayout(renderToolsLayout)

        self.layout.addWidget(self.debugLabel)

        self.layout.addWidget(self.verboseCB)



        # Verbose

	if self.verboseCB.isChecked():

            print "espnMatteTagsUI Loaded"





	

    ####################################################################################################

    # addVrayUserAttributes()

    # adds vrayUserAttributes to selected objects if it does not already exist.

    ####################################################################################################  

    def addVrayUserAttributes(self):



	if self.verboseCB.isChecked(): print("\nAdding vrayUserAttributes...")



        shapes = cmds.ls(sl=1, dag=1, lf=1, s=1)



        if shapes:

            for shape in shapes:

                if not cmds.objExists('%s.vrayUserAttributes' %shape):

                    cmds.vray("addAttributesFromGroup", shape, "vray_user_attributes", 1)

	            if self.verboseCB.isChecked(): print "vrayUserAttributes added to:", shape

                else:

	            if self.verboseCB.isChecked(): print "vrayUserAttributes already exists on:", shape

        else:

            print "Nothing Selected"







    ####################################################################################################

    # getVrayUserAttributes()

    # 

    ####################################################################################################  

    def getVrayUserAttributes(self):



	if self.verboseCB.isChecked(): print("\nGetting Vray User Attributes...")



	shapes = cmds.ls(sl=1, dag=1, lf=1, s=1)

	attributeList = []



        if shapes:

            for shape in shapes:

                if cmds.objExists('%s.vrayUserAttributes' %shape):

		    if cmds.getAttr('%s.vrayUserAttributes' %shape):

                        attributeList = cmds.getAttr('%s.vrayUserAttributes' %shape);

	                if self.verboseCB.isChecked(): print "Retrieved attributes from ", shape, ":", attributeList

                    else:

	                if self.verboseCB.isChecked(): print "Node:", shape, "has no attributes assigned yet"

                else: 

                    if self.verboseCB.isChecked(): print "Node:", shape, "does not have vrayUserAttributes"



            #if attributeList:

               #self.tagsLE.setText(attributeList)

            if not attributeList:

                if self.verboseCB.isChecked(): print "No vrayUserAttributes found in selection"

        else:

            print "Nothing Selected"



        return attributeList







    ####################################################################################################

    # setVrayUserAttributes()

    # 

    ####################################################################################################  

    def setVrayUserAttributes(self, attributeList):



	if self.verboseCB.isChecked(): print("\nSetting Vray User Attributes...")



        # Enforce terminating semicolon, the ghetto way

        attributeList = attributeList.strip(';')

        attributeList = attributeList + ';'



	shapes = cmds.ls(sl=1, dag=1, lf=1, s=1)



        if shapes:

	    for shape in shapes:

                if cmds.objExists('%s.vrayUserAttributes' %shape):

                    if self.verboseCB.isChecked(): print ("Tagging with %s" %attributeList);

                    cmds.setAttr(('%s.vrayUserAttributes' %shape), attributeList, type='string');

                else:

                    if self.verboseCB.isChecked(): print "Node:", shape, "does not have vrayUserAttributes"

        else:

            print "Nothing Selected"





    ####################################################################################################

    # parseVrayUserAttributes()

    # Selects all geometry in the scene and generates a list of all vrayUserAttributes found

    ####################################################################################################      	
    @classmethod
    def parseVrayUserAttributes(self):



	# Select all shape nodes in the scene

	geometry = cmds.ls(geometry=True)

	shapes = cmds.listRelatives(geometry, p=True, path=True)

	cmds.select(shapes, r=True)



	# Declare variables

	allAttributes= []

	count = 0



	# For each node selected...

        for shape in shapes:

	    attributeList = []



    	    if cmds.objExists('%s.vrayUserAttributes' %shape):

                attributeString = cmds.getAttr('%s.vrayUserAttributes' %shape)

                attributeList = tokenizeVrayUserAttributes(attributeString)



	    for attr in attributeList:

		allAttributes.append(attr)

	

            count = count+1;





	# Remove duplicate vrayUserAttributes from list (There will be a lot!)

	allAttributes = remove_duplicates(allAttributes)





	# Verbose

	#if self.verboseCB.isChecked():

    #        print "Found the following vrayUserAttributes on", count, "Objects:"

	#   for attr in allAttributes:

	#       print attr



	return allAttributes;







    ####################################################################################################

    # createRenderElements()

    # Creates Render Elements and User Color nodes given a supplied list of attribute names

    ####################################################################################################  
    @classmethod
    def createRenderElements(self, attributeList):



	if not attributeList:

	    print "No vrayUserAttributes"

	    return



	cBlack = 0;

	cmds.sets(n='espnMatteTagSet', em=True)

	cmds.sets(n='espnMatteTagUCSet', em=True)

	cmds.sets(n='espnMatteTagRESet', em=True)



	for attribute in attributeList:

            matteName = ('m_%s' %attribute)



	    # Create Vray User Color Node to link tags with their respective Render Element

	    userColor = mel.eval('shadingNode -asUtility VRayUserColor;')

	    cmds.setAttr(userColor + '.userAttribute', '%s' %attribute, type = 'string')

	    cmds.setAttr(userColor + '.color', 0.0, 0.0, 0.0, type = 'double3')



	    # Create Vray Render Element

	    renderElement = mel.eval('vrayAddRenderElement ExtraTexElement;')

	    cmds.setAttr(renderElement + '.vray_explicit_name_extratex', matteName, type = 'string')



    	    # Connect User Color to Render Element

            cmds.connectAttr('%s.outColor' %userColor ,'%s.vray_texture_extratex' %renderElement);



	    cmds.sets(userColor, add='espnMatteTagUCSet')

 	    cmds.sets(renderElement, add='espnMatteTagRESet') 



	    # Rename both ndoes now that connections have been made

	    cmds.rename(renderElement, matteName);

	    cmds.rename(userColor, 'uc%s' %attribute);



	cmds.sets('espnMatteTagUCSet', add='espnMatteTagSet')

	cmds.sets('espnMatteTagRESet', add='espnMatteTagSet')







    ####################################################################################################

    # btnAddVrayUserAttributes()

    # Helper function that activates on "Add Vray User Attributes" button

    ####################################################################################################  

    def btnAddVrayUserAttributes(self):

        self.addVrayUserAttributes()









    ####################################################################################################

    # btnSetVrayUserAttributes()

    # Helper function that activates on "Set Vray User Attributes" button

    ####################################################################################################  

    def btnSetVrayUserAttributes(self):

	attributeList = self.tagsLE.text()

        self.setVrayUserAttributes(attributeList)





    ####################################################################################################

    # btnGetVrayUserAttributes()

    # Helper function that activates on "Add Vray User Attributes" button

    ####################################################################################################  

    def btnGetVrayUserAttributes(self):

        attributeList = self.getVrayUserAttributes()

        self.tagsLE.setText(attributeList)





    ####################################################################################################

    # btnAppendVrayUserAttributes()

    # Helper function that activates on "Add Vray User Attributes" button

    ####################################################################################################  

    def btnAppendVrayUserAttributes(self):



        # Feature request: Check if tag already exists and do not replace



        inputTags = self.tagsLE.text()

        if (inputTags):

           

            attributeList = self.getVrayUserAttributes()

            if not attributeList:

                attributeList = inputTags



	        if self.verboseCB.isChecked():

                    print "btnAppendVrayUserAttributes: No existing attributes, creating new attribute list: " + attributeList

                    print attributeList

            else:

                # Enforce terminating semicolon, the ghetto way

                attributeList = attributeList.strip(';')

                attributeList = attributeList + ';'

                attributeList = attributeList + inputTags



	        if self.verboseCB.isChecked():

                    print "btnAppendVrayUserAttributes: Appending tags to attribute list: " + attributeList



            self.setVrayUserAttributes(attributeList)



        else:

	    if self.verboseCB.isChecked():

                print "btnAppendVrayUserAttributes: Nothing to append"







    ####################################################################################################

    # btnCreateRenderElements()

    # Helper function that activates on "Create Render Elements" button

    ####################################################################################################  

    def btnCreateRenderElements(self):

        attributeList = self.parseVrayUserAttributes()

	self.createRenderElements(attributeList)





    ####################################################################################################

    # btnDestroyRenderElements()

    # Helper function that activates on "Destroy Render Elements" button

    ####################################################################################################  

    def btnDestroyRenderElements(self):

        cmds.select( 'espnMatteTagSet' )

        cmds.delete()







    ####################################################################################################

    # cbVerboseMode()

    # Helper function that activates on checking/unchecking "Verbose" check box

    ####################################################################################################  

    def cbVerboseMode(self, state):

        if state == 0:

            print "\nExiting Verbose Mode..."

            print "##################################################\n";

        else:

            print "##################################################";

            print "Entering Verbose Mode...\n"







    ####################################################################################################

    # closeEvent()

    # 

    ####################################################################################################  

    def closeEvent(self, event):

	if self.verboseCB.isChecked():

            print "espnMatteTagsUI Window Closed."

            print "##################################################\n\n";







####################################################################################################

# tokenizeVrayUserAttributes()

# Given a typical vrayUserAttributes string (eg. "Metal=1;Signage=1;") Returns a tokenized 

# Python List of said attributes

#################################################################################################### 

def tokenizeVrayUserAttributes(theText):

    theList = theText.split(';')

    strippedList = []



    # Removes empty items from list (Usually caused by terminating ";" in vrayUserAttribute List)

    theList = filter(None, theList)



    # Strips "=1" from each vrayUserAttribute

    for str in theList:

	strippedStr = str.strip( '=1' )

	strippedList.append(strippedStr)



    return strippedList;







####################################################################################################

# remove_duplicates()

# Removes duplicate entries in a given list WITHOUT reordering the elements

#################################################################################################### 

def remove_duplicates(myList):

     output = []

     seen = set()

     for value in myList:

        if value not in seen:

            output.append(value)

            seen.add(value)



     return output







####################################################################################################

# main()

#################################################################################################### 

def main():

    ui = espnMatteTags()

    ui.show()

    return ui





if __name__ == '__main__':

    main()