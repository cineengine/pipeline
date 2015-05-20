#Nuke Wedge Functionality for ESPN
import nuke
import os
from pipeline.nuke import switchTeam

def preRender():
	import nuke
	import os
	from pipeline.nuke import switchTeam
	masterWrite = nuke.toNode('MASTER_WRITE')
	if not masterWrite.knob('DisablePermuting').getValue():
		fileKnob = masterWrite.knob('file')
		templateFileNameKnob = masterWrite.knob('TemplateFileName')
		knobNames = masterWrite.knobs().keys()
		iteratorKeys = []
		nonPermutingIteratorKeys = []
		indices = {}
		lists = {}
		splitLists = {}
		currents = {}
		nonPermutingCurrents = {}
		for knob in knobNames:
		    if 'Index' in knob or 'List' in knob or 'Current' in knob:
		        knobRoot = knob.split('Index')[0].split('List')[0].split('Current')[0]
		        if (knobRoot + 'Index') in knobNames and (knobRoot + 'List') in knobNames and (knobRoot + 'Current') in knobNames:
		            if knobRoot in iteratorKeys:
		                knobRoot = knobRoot
		            else:
		                iteratorKeys.append(knobRoot)
		                indices[knobRoot] = masterWrite.knob(knobRoot + 'Index')
		                lists[knobRoot] = masterWrite.knob(knobRoot + 'List')
		                splitLists[knobRoot] = (masterWrite.knob(knobRoot + 'List').getValue().split(','))
		                currents[knobRoot] = masterWrite.knob(knobRoot + 'Current')
		        else:
		        	if (knobRoot + 'Index') in knobNames and (knobRoot + 'Current') in knobNames:
		        		if knobRoot in nonPermutingIteratorKeys:
		        			knobRoot = knobRoot
		        		else:
		        			nonPermutingIteratorKeys.append(knobRoot)
		        			nonPermutingCurrents[knobRoot] = masterWrite.knob(knobRoot + 'Current')
		#initialized setup
		switchTeam.loadTeam(matchup=nuke.toNode('MASTER_CTRL').knob('isMatchup').getValue())
		filepath = templateFileNameKnob.getValue()
		for key in iteratorKeys:
		    currents[key].setValue(splitLists[key][int(indices[key].getValue())])
		    filepath = filepath.replace('<' + key.lower() + '>',currents[key].getValue().upper())
		for key in nonPermutingIteratorKeys:
			filepath = filepath.replace('<' + key.lower() + '>',nonPermutingCurrents[key].getValue().upper())
		fileKnob.setValue(filepath)
		try:
			os.makedirs(nuke.callbacks.filenameFilter(os.path.dirname(nuke.filename(nuke.thisNode()))))
		except:
			pass

def preFrame():
	import nuke
	import os
	from pipeline.nuke import switchTeam
	masterWrite = nuke.toNode('MASTER_WRITE')
	if not masterWrite.knob('DisablePermuting').getValue():
		fileKnob = masterWrite.knob('file')
		templateFileNameKnob = masterWrite.knob('TemplateFileName')
		knobNames = masterWrite.knobs().keys()
		iteratorKeys = []
		nonPermutingIteratorKeys = []
		indices = {}
		lists = {}
		splitLists = {}
		currents = {}
		nonPermutingCurrents = {}
		for knob in knobNames:
		    if 'Index' in knob or 'List' in knob or 'Current' in knob:
		        knobRoot = knob.split('Index')[0].split('List')[0].split('Current')[0]
		        if (knobRoot + 'Index') in knobNames and (knobRoot + 'List') in knobNames and (knobRoot + 'Current') in knobNames:
		            if knobRoot in iteratorKeys:
		                knobRoot = knobRoot
		            else:
		                iteratorKeys.append(knobRoot)
		                indices[knobRoot] = masterWrite.knob(knobRoot + 'Index')
		                lists[knobRoot] = masterWrite.knob(knobRoot + 'List')
		                splitLists[knobRoot] = (masterWrite.knob(knobRoot + 'List').getValue().split(','))
		                currents[knobRoot] = masterWrite.knob(knobRoot + 'Current')
		        else:
		        	if (knobRoot + 'Index') in knobNames and (knobRoot + 'Current') in knobNames:
		        		if knobRoot in nonPermutingIteratorKeys:
		        			knobRoot = knobRoot
		        		else:
		        			nonPermutingIteratorKeys.append(knobRoot)
		        			nonPermutingCurrents[knobRoot] = masterWrite.knob(knobRoot + 'Current')
		#initialized setup
		switchTeam.loadTeam(matchup=nuke.toNode('MASTER_CTRL').knob('isMatchup').getValue())
		filepath = templateFileNameKnob.getValue()
		for key in iteratorKeys:
		    currents[key].setValue(splitLists[key][int(indices[key].getValue())])
		    filepath = filepath.replace('<' + key.lower() + '>',currents[key].getValue().upper())
		for key in nonPermutingIteratorKeys:
			filepath = filepath.replace('<' + key.lower() + '>',nonPermutingCurrents[key].getValue().upper())
		fileKnob.setValue(filepath)
		try:
			os.makedirs(nuke.callbacks.filenameFilter(os.path.dirname(nuke.filename(nuke.thisNode()))))
		except:
			pass

def postFrame():
	import nuke
	import os, time
	from pipeline.nuke import switchTeam
	masterWrite = nuke.toNode('MASTER_WRITE')
	if not masterWrite.knob('DisablePermuting').getValue():
		fileKnob = masterWrite.knob('file')
		templateFileNameKnob = masterWrite.knob('TemplateFileName')
		knobNames = masterWrite.knobs().keys()
		iteratorKeys = []
		nonPermutingIteratorKeys = []
		indices = {}
		lists = {}
		splitLists = {}
		currents = {}
		nonPermutingCurrents = {}
		for knob in knobNames:
		    if 'Index' in knob or 'List' in knob or 'Current' in knob:
		        knobRoot = knob.split('Index')[0].split('List')[0].split('Current')[0]
		        if (knobRoot + 'Index') in knobNames and (knobRoot + 'List') in knobNames and (knobRoot + 'Current') in knobNames:
		            if knobRoot in iteratorKeys:
		                knobRoot = knobRoot
		            else:
		                iteratorKeys.append(knobRoot)
		                indices[knobRoot] = masterWrite.knob(knobRoot + 'Index')
		                lists[knobRoot] = masterWrite.knob(knobRoot + 'List')
		                splitLists[knobRoot] = (masterWrite.knob(knobRoot + 'List').getValue().split(','))
		                currents[knobRoot] = masterWrite.knob(knobRoot + 'Current')
		        else:
		        	if (knobRoot + 'Index') in knobNames and (knobRoot + 'Current') in knobNames:
		        		if knobRoot in nonPermutingIteratorKeys:
		        			knobRoot = knobRoot
		        		else:
		        			nonPermutingIteratorKeys.append(knobRoot)
		        			nonPermutingCurrents[knobRoot] = masterWrite.knob(knobRoot + 'Current')
		#initialized setup

		finishedRenderPermutations = True
		renderString = '---N:' + masterWrite.name() + '---F:' + str(nuke.frame())
		for key in iteratorKeys:
			if int(indices[key].getValue())+1<len(splitLists[key]):
				finishedRenderPermutations = False
			renderString = renderString + '---' + key.upper() + ":" + currents[key].getValue()

		if not finishedRenderPermutations:
			import threading, thread
			renderThread = threading.Thread(name='writeFunc', target=writeFunc, args=(masterWrite, nuke.frame(), nuke.frame(), renderString))
			renderThread.setDaemon(False)
			print 'New Render Thread starting'
			renderThread.start()
			#renderThread.join()
			#print 'New Render Thread joined'
			while renderThread.isAlive():
				time.sleep(1.0)
				print 'Thread is still alive'
			#bgID = nuke.executeBackgroundNuke(exe_path=nuke.EXE_PATH, nodes=[masterWrite], frameRange=nuke.FrameRanges(str(nuke.frame())), views=['main'], continueOnError=True, limits={'maxThreads':0, 'maxCache':'32G'} )
			#if bgID == -1:
			#	print "Failed BG Render"
			#nuke.executeInMainThreadWithResult(writeFunc, args=(masterWrite, nuke.frame(), nuke.frame()))

'''def writeFunc(writeNode, startFrame, endFrame, renderString):
	import time
	import threading, thread
	import traceback 
	import types 
	import _nuke 
	print 'rendering ' + renderString + '\n'
	print writeNode.name()
	print str(startFrame) + ',' + str(endFrame)
	#nuke.executeInMainThread(nuke.execute, args=(writeNode, startFrame, endFrame), kwargs={'continueOnError':False})
	#nuke.execute(writeNode, startFrame, endFrame)
	 
	#def executeInMainThreadWithResult( call, args = (), kwargs = {}): 
	call = nuke.execute
	args = (writeNode, startFrame, endFrame)
	kwargs = {'continueOnError':False}

	if type(args) != types.TupleType: 
		args = (args,) 
	print "args = " + str(args)
	resultEvent = threading.Event() 
	print "resultEvent: " + str(resultEvent)
	id = _nuke.RunInMainThread.request(call, args, kwargs, resultEvent ) 
	print "id: " + str(id)
	resultEvent.wait()
	r = None
	while(r is None):
		print "Waiting for Sub-Render Result"
		time.sleep(1.0)
		try:
			r = _nuke.RunInMainThread.result(id)
		except:
			print "Failed waiting"
			traceback.print_exc()
	try: 
		print "Trying main thread call"
		r = _nuke.RunInMainThread.result(id) 
	except: 
		print "Failed main thread call"
		traceback.print_exc() 
		r = None 

	print 'rendered  ' + renderString + '\n'
	print "type: " + str(type(r)) + "result: " + str(r)
	#return r
	return 1
'''

def writeFunc(writeNode, startFrame, endFrame, renderString):
	import time
	import threading, thread
	print 'rendering ' + renderString + '\n'
	print writeNode.name()
	print str(startFrame) + ',' + str(endFrame)
	nuke.executeInMainThread(nuke.execute, args=(writeNode, startFrame, endFrame), kwargs={'continueOnError':False})
	#nuke.execute(writeNode, startFrame, endFrame)
	print 'rendered  ' + renderString + '\n'
	return 1

def postRender():
	import nuke
	import os
	from pipeline.nuke import switchTeam
	masterWrite = nuke.toNode('MASTER_WRITE')
	if not masterWrite.knob('DisablePermuting').getValue():
		fileKnob = masterWrite.knob('file')
		templateFileNameKnob = masterWrite.knob('TemplateFileName')
		knobNames = masterWrite.knobs().keys()
		iteratorKeys = []
		nonPermutingIteratorKeys = []
		indices = {}
		lists = {}
		splitLists = {}
		currents = {}
		nonPermutingCurrents = {}
		for knob in knobNames:
		    if 'Index' in knob or 'List' in knob or 'Current' in knob:
		        knobRoot = knob.split('Index')[0].split('List')[0].split('Current')[0]
		        if (knobRoot + 'Index') in knobNames and (knobRoot + 'List') in knobNames and (knobRoot + 'Current') in knobNames:
		            if knobRoot in iteratorKeys:
		                knobRoot = knobRoot
		            else:
		                iteratorKeys.append(knobRoot)
		                indices[knobRoot] = masterWrite.knob(knobRoot + 'Index')
		                lists[knobRoot] = masterWrite.knob(knobRoot + 'List')
		                splitLists[knobRoot] = (masterWrite.knob(knobRoot + 'List').getValue().split(','))
		                currents[knobRoot] = masterWrite.knob(knobRoot + 'Current')
		        else:
		        	if (knobRoot + 'Index') in knobNames and (knobRoot + 'Current') in knobNames:
		        		if knobRoot in nonPermutingIteratorKeys:
		        			knobRoot = knobRoot
		        		else:
		        			nonPermutingIteratorKeys.append(knobRoot)
		        			nonPermutingCurrents[knobRoot] = masterWrite.knob(knobRoot + 'Current')
		#initialized setup

		carryFlag = False
		firstFlag = True

		for key in iteratorKeys:
			if firstFlag or carryFlag:
				indices[key].setValue(int(indices[key].getValue()) + 1)
				firstFlag = False
			if indices[key].getValue()>=len(splitLists[key]):
				carryFlag = True
				indices[key].setValue(0)
			else:
				carryFlag = False
		if carryFlag:
			for key in iteratorKeys:
				indices[key].setValue(0)
			print "FINISHED WEDGE FRAME: " + str(nuke.frame())

def initialSetup():
	import nuke
	masterWrite = nuke.toNode('MASTER_WRITE')
	addPermutor = nuke.PyScript_Knob('NewPermutor', 'NewPermutor')
	addPermutor.setCommand('wedge.knobSetup()')
	masterWrite.addKnob(addPermutor)
	permutorSwitch = nuke.PyScript_Knob('PermutorSwitch', 'PermutorSwitch')
	permutorSwitch.setCommand('wedge.permutorSwitch()')
	masterWrite.addKnob(permutorSwitch)
	farmWrites = nuke.PyScript_Knob('FarmWrites', 'FarmWrites')
	farmWrites.setCommand('wedge.setupDeadlineRenderNodes()')
	masterWrite.addKnob(farmWrites)

	beforeRender = masterWrite.knob('beforeRender')
	beforeFrameRender = masterWrite.knob('beforeFrameRender')
	afterFrameRender = masterWrite.knob('afterFrameRender')
	afterRender = masterWrite.knob('afterRender')
	beforeRender.setValue('wedge.preRender()')
	beforeFrameRender.setValue('wedge.preFrame()')
	afterFrameRender.setValue('wedge.postFrame()')
	afterRender.setValue('wedge.postRender()')

	templateFileKnob = nuke.File_Knob('TemplateFileName','TemplateFileName')
	wedgeLabels = nuke.Boolean_Knob('WedgeLabels','WedgeLabels')
	masterWrite.addKnob(templateFileKnob) 
	masterWrite.addKnob(wedgeLabels)

def knobSetup():
	import nuke
	txt = nuke.getInput('New Permutor', 'Name')
	if txt:
		masterWrite = nuke.toNode('MASTER_WRITE')
		listKnob = nuke.String_Knob(txt+'List', txt+'List') 
		currentKnob = nuke.String_Knob(txt+'Current', txt+'Current') 
		indexKnob = nuke.Int_Knob(txt+'Index', txt+'Index') 
		masterWrite.addKnob(listKnob) 
		masterWrite.addKnob(currentKnob) 
		masterWrite.addKnob(indexKnob)
		indexKnob.setValue(0)

def permutorSwitch():
	import nuke
	for each in nuke.allNodes():
		each.knob("selected").setValue(False)
	txt = nuke.getInput('Select Permutor', '')
	if txt:
		masterWrite = nuke.toNode('MASTER_WRITE')
		switch = nuke.createNode('Switch')
		switch.knob('which').setExpression('[value MASTER_WRITE.' + txt + 'Index]')

		nuke.Node.setXYpos(switch, masterWrite.xpos()+100, masterWrite.ypos()+100)

def setupDeadlineRenderNodes():
	import nuke, nukescripts
	import os
	#from pipeline.nuke import switchTeam
	masterWrite = nuke.toNode('MASTER_WRITE')
	writeSource = masterWrite.input(0)
	fileKnob = masterWrite.knob('file')
	templateFileNameKnob = masterWrite.knob('TemplateFileName')
	knobNames = masterWrite.knobs().keys()
	iteratorKeys = []
	nonPermutingIteratorKeys = []
	indices = {}
	lists = {}
	splitLists = {}
	currents = {}
	nonPermutingCurrents = {}
	for knob in knobNames:
	    if 'Index' in knob or 'List' in knob or 'Current' in knob:
	        knobRoot = knob.split('Index')[0].split('List')[0].split('Current')[0]
	        if (knobRoot + 'Index') in knobNames and (knobRoot + 'List') in knobNames and (knobRoot + 'Current') in knobNames:
	            if knobRoot in iteratorKeys:
	                knobRoot = knobRoot
	            else:
	                iteratorKeys.append(knobRoot)
	                indices[knobRoot] = masterWrite.knob(knobRoot + 'Index')
	                lists[knobRoot] = masterWrite.knob(knobRoot + 'List')
	                splitLists[knobRoot] = (masterWrite.knob(knobRoot + 'List').getValue().split(','))
	                currents[knobRoot] = masterWrite.knob(knobRoot + 'Current')
	        else:
	        	if (knobRoot + 'Index') in knobNames and (knobRoot + 'Current') in knobNames:
	        		if knobRoot in nonPermutingIteratorKeys:
	        			knobRoot = knobRoot
	        		else:
	        			nonPermutingIteratorKeys.append(knobRoot)
	        			nonPermutingCurrents[knobRoot] = masterWrite.knob(knobRoot + 'Current')
	#initialized setup

	renderNodeCount = 1

	for key in iteratorKeys:
		indices[key].setValue(0)

	carryFlag = False
	firstFlag = True

	while not carryFlag:
		carryFlag = False
		firstFlag = True
		for key in iteratorKeys:
			if firstFlag or carryFlag:
				indices[key].setValue(int(indices[key].getValue()) + 1)
				firstFlag = False
			if indices[key].getValue()>=len(splitLists[key]):
				carryFlag = True
				indices[key].setValue(0)
			else:
				carryFlag = False

		nodeSuffix = ''
		for key in iteratorKeys:
			nodeSuffix = nodeSuffix + '_' + splitLists[key][ int(indices[key].getValue()) ]

		#Write nodes
		nukescripts.clear_selection_recursive()
		writeNode = nuke.createNode('Write')
		writeNode.setInput(0, writeSource)
		preUpdateString = ''
		for key in iteratorKeys:
			preUpdateString = preUpdateString + 'nuke.toNode(\'MASTER_WRITE\').knob(\'' + key + 'Index' + '\').setValue(' + str(int(indices[key].getValue())) + ')' + ';'
			preUpdateString = preUpdateString + 'nuke.toNode(\'MASTER_WRITE\').knob(\'' + key + 'Current' + '\').setValue(\'' + str(splitLists[key][int(indices[key].getValue())]) + '\')' + ';'
		updateString = 'self.knob(\'file\').setValue(nuke.toNode(\'MASTER_WRITE\').knob(\'file\').getValue())'
		updateString = updateString.replace( 'self', 'nuke.toNode(\'' + masterWrite.name() + nodeSuffix + '\')' )
		writeNode.knob('beforeRender').setValue(preUpdateString + 'wedge.preRender();' + ';' + updateString)
		writeNode.knob('beforeFrameRender').setValue(preUpdateString + 'wedge.preFrame();' + ';' + updateString)
		nuke.Node.setXYpos( writeNode, masterWrite.xpos()+renderNodeCount*100, masterWrite.ypos() )
		writeNode.knob('name').setValue(masterWrite.name() + nodeSuffix)
		renderNodeCount = renderNodeCount + 1

	if carryFlag:
		for key in iteratorKeys:
			indices[key].setValue(0)
