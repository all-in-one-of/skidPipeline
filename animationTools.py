# ****************************************** S K I D     A N I M     T O O L S ******************************************

import maya.cmds as cmds
import maya.mel as mel
import commonTools
import os
import sys
from pymel.core import *

# ****************************************** F U N C T I O N S ******************************************

def createSpeedAttribute(*args):
	'''This will create an attribute on any object which shows its speed in kmh at current frame'''
	sel = cmds.ls(selection=True)
	if len(sel) != 1 :
		cmds.warning('One object must be selected')
	else :
		sel = sel[0]
		cmds.addAttr(sel,ln='speed',nn='Speed (kmh)',at='double',dv=0,h=False,k=True)
		cmds.expression(s="float $lastPosX = `getAttr -t (frame-1) "+sel+".tx`;\nfloat $lastPosY = `getAttr -t (frame-1) "+sel+".ty`;\nfloat $lastPosZ = `getAttr -t (frame-1) "+sel+".tz`;\n\nfloat $tempSpeed = abs (mag (<<"+sel+".translateX,"+sel+".translateY,"+sel+".translateZ>>)- mag (<<$lastPosX,$lastPosY,$lastPosZ>>) );\n\n"+sel+".speed = ((($tempSpeed/100)*24)*3.6)",ae=1,uc='all')
		cmds.select(sel,r=True)

def exportAbcRfM(*args):
	'''This will open the alembic export window and include Renderman attributes'''
	try:
		import sys
		rmScripts = os.path.abspath('C:/Program Files/Pixar/RenderManForMaya-22.1/scripts/rfm2/utils')
		sys.path.insert(0,rmScripts)
		import abc_support
		abc_support.export(False, True)
	except NameError:
		import maya.cmds
		import maya.utils
		maya.utils.executeDeferred('''maya.cmds.loadPlugin('RenderMan_for_Maya.py')''')

def playblastAnim(publish,*args):
	'''This will make a playblast of the timeline and version it
	publish must be a boolean'''
	sceneFullName = cmds.file(q=1,sn=1,shn=1)
	videoPath = os.path.abspath(cmds.workspace(sn=True,q=True)+'/video/'+sceneFullName)
	if publish == False:
		playblastPath = videoPath.split('.ma')
		playblastPath = playblastPath[0]
		playblastPath = os.path.abspath(playblastPath)+'.mov'
		playblastPath = os.path.abspath(playblastPath)
	else :
		editDir = '//merlin/3D4/skid/07_editing/input/03_spline/'
		scenePath = cmds.workspace(sn=True,q=True)
		sceneName = os.path.split(scenePath)[1]
		playblastPath = editDir + sceneName + '/' + sceneName

	# 1. check if version already has playblast
	if os.path.isfile(playblastPath) or os.path.isfile(playblastPath+'.1001.jpg'):
		confirm = cmds.confirmDialog (title='Playblast', \
			message= 'A playblast already exists for this version. Replace ?', \
			button=['Continue','Cancel'], defaultButton='Continue', cancelButton='Cancel', dismissString='Cancel' )
		if confirm != 'Continue':
			sys.exit()

	# 2. Set a number of attributes before playblast
	# Pause viewport
	cmds.refresh(suspend=True) 
	# Generate viewport textures
	mel.eval("generateAllUvTilePreviews;")

	scenePath = os.path.abspath(cmds.workspace(sn=True,q=True))
	sceneName = os.path.split(scenePath)
	shotCam = sceneName[1]
	# Keep camera attributes to reset them after playblast
	camDFG = cmds.getAttr(shotCam+'.displayFilmGate')
	camDR = cmds.getAttr(shotCam+'.displayResolution')
	camDGM = cmds.getAttr(shotCam+'.displayGateMask')
	camOS = cmds.getAttr(shotCam+'.overscan')
	# Set attributes
	cmds.setAttr(shotCam+'.displayFilmGate',0)
	cmds.setAttr(shotCam+'.displayResolution',0)
	cmds.setAttr(shotCam+'.displayGateMask',0)
	# Fix camera overscan
	camDriven = cmds.listConnections(shotCam+'.overscan',plugs=True)
	if camDriven != None:
		for i in camDriven :
			cmds.disconnectAttr(i,shotCam+'.overscan')
	cmds.setAttr(shotCam+'.overscan',1)
	cmds.setAttr("hardwareRenderingGlobals.multiSampleEnable",1)
	cmds.setAttr('hardwareRenderingGlobals.multiSampleCount',16)
	# cmds.setAttr("hardwareRenderingGlobals.motionBlurEnable",1)
	# cmds.setAttr('hardwareRenderingGlobals.motionBlurSampleCount',16)
	cmds.setAttr('hardwareRenderingGlobals.ssaoEnable',1)
	cmds.setAttr('hardwareRenderingGlobals.ssaoSamples',32)
	cmds.setAttr('hardwareRenderingGlobals.ssaoRadius',64)
	cmds.setAttr('hardwareRenderingGlobals.ssaoFilterRadius',32)

	mel.eval('setObjectDetailsVisibility(0);') # Object Details
	mel.eval('setCameraNamesVisibility(1);') # Camera Name
	mel.eval('setCurrentFrameVisibility(1);') # Current Frame
	mel.eval('setFocalLengthVisibility(1);') # Focal length
	mel.eval('setFrameRateVisibility(0);') # FPS

	# Viewport hide all but geometries
	viewport = cmds.getPanel(withFocus=True)
	cmds.modelEditor(viewport,e=1,allObjects=0)
	cmds.modelEditor(viewport,e=1, \
		pluginObjects=('gpuCacheDisplayFilter',1), \
		polymeshes=1, \
		displayTextures=1, \
		imagePlane=1)

	# Do playblast
	if publish == False :
		cmds.playblast(format="qt", \
			filename=playblastPath, \
			forceOverwrite=True, \
			sequenceTime=0, \
			clearCache=1, \
			viewer=0, \
			showOrnaments=1, \
			offScreen=True, \
			fp=4, \
			percent=100, \
			compression="H.264", \
			quality=100, \
			widthHeight=[2048,858])
	else :
		cmds.playblast(format="image", \
			filename=playblastPath, \
			forceOverwrite=True, \
			sequenceTime=0, \
			clearCache=1, \
			viewer=0, \
			showOrnaments=1, \
			offScreen=True, \
			fp=4, \
			percent=100, \
			compression="jpg", \
			quality=100, \
			widthHeight=[2048,858])
		
	# Reset attributes
	cmds.setAttr(shotCam+'.displayFilmGate',camDFG)
	cmds.setAttr(shotCam+'.displayResolution',camDR)
	cmds.setAttr(shotCam+'.displayGateMask',camDGM)
	cmds.setAttr(shotCam+'.overscan',camOS)

	# cmds.setAttr("hardwareRenderingGlobals.motionBlurEnable",0)
	cmds.setAttr('hardwareRenderingGlobals.ssaoEnable',0)
	cmds.setAttr("hardwareRenderingGlobals.multiSampleEnable",0)

	# viewport display all, disable textures
	cmds.modelEditor(viewport, \
		e=1, \
		allObjects=1, \
		displayTextures=0)
	# Unpause viewport
	cmds.refresh(suspend=False)

	# Read playblast
	if publish == False :
		os.startfile(playblastPath)

def publishAnimations(*args):
	'''This will publish the selected sets using maya 
	standalone and automatically backup any previously published animation'''
	import subprocess

	selectionSets = cmds.ls(selection=True)

	# Check if save has unsaved changes
	if cmds.file(q=True,modified=True) :
		cmds.warning('Save your scene before publishing')
		return

	# Check something is selected
	if not selectionSets :
		cmds.warning('Nothing is selected')
		return

	# Check only one asset is selected
	ns = []
	for i in selectionSets :
		i = i.split(':')[0]
		ns.append(i)
	ns = list(dict.fromkeys(ns))
	if len(ns) > 1 :
		cmds.warning('Selection sets from different assets are selected')
		return

	# Check if published alembic file is already in use
	scenePath = os.path.abspath(cmds.workspace(sn=True,q=True))
	scenePath = scenePath.replace(os.sep, '/')
	asset = ns[0].split('_')[0]
	
	# override namespace if asset is propsOpponentsCar
	if asset == 'propsOpponentsCar':
		asset = ns[0].split('_')[0] + ns[0].split('_rig')[1]

	abcFile = scenePath + '/abc/' + asset + '.abc'
	if os.path.isfile(abcFile):
		try :
			os.rename(abcFile,abcFile)
		except WindowsError, e :
			cmds.warning('Published alembic is already open in another application and cant be replaced.')
			return

	# prepare confirm dialog
	frameRange = str(cmds.playbackOptions(q=True,ast=True)) + '-' + str(cmds.playbackOptions(q=True,aet=True))
	sceneFile = cmds.file(query=True,sceneName=True)

	# confirm dialog
	confirm = cmds.confirmDialog( title='Publish Animation', \
		message='This will replace any previously published animation. Check your parameters : \n\nSCENE FILE :\n %s \n\nASSET : \n%s \n\nSELECTION SETS : \n%s \n\nFRAME RANGE : \n%s' %(sceneFile,asset,selectionSets,frameRange), \
		button=['Continue','Cancel'], \
		defaultButton='Continue', \
		cancelButton='Cancel', \
		dismissString='Cancel' )
	if confirm != 'Continue':
		return

	# fire mayapy
	publishScript = '//Merlin/3d4/skid/09_dev/toolScripts/publish/mayapy/publishAnim.py'
	subprocess.Popen(['mayapy',publishScript,sceneFile,asset]+selectionSets)


def toggleConstraintCar(asset,*args):
	attrList = [ \
	asset+'_rig:CTRL_roue_RR_offset_parentConstraint1.Fit_to_ground_RRW0', \
	asset+'_rig:CTRL_roue_RL_offset_parentConstraint1.Fit_to_ground_RLW0', \
	asset+'_rig:CTRL_roue_FL_offset_parentConstraint1.Fit_to_ground_FLW0', \
	asset+'_rig:CTRL_roue_FR_offset_parentConstraint1.Fit_to_ground_FRW0' ]

	for attr in attrList :
		if cmds.getAttr(attr) == 0 :
			cmds.setAttr(attr,1)
		else :
			cmds.setAttr(attr,0)

def poseCar(asset,*args):
	cmds.loadPlugin('atomImportExport.mll')
	cmds.select(asset+'_rig:CTRL',r=True)
	cmds.file('//merlin/3d4/skid/04_asset/character/'+asset+'/data/startPose.atom',  \
		i=True, \
		type='atomImport', \
		ra=True, \
		namespace='poseCar', \
		options=';;targetTime=3;option=scaleReplace;match=hierarchy;;selected=selectedOnly;search=;replace=;prefix=;suffix=;mapFile=;')
	cmds.select(asset+'_rig:CTRL',r=True)

def publishCamera(*args):
	from shutil import copyfile

	scenePath = os.path.abspath(cmds.workspace(sn=True,q=True))
	sceneName = os.path.split(scenePath)
	shotCam = sceneName[1]

	if not cmds.objExists(shotCam):
		cmds.warning('No camera matches name '+shotCam)
		return

	abcFile = scenePath+'/abc/'+shotCam+'.abc'
	frameRange = str(cmds.playbackOptions(q=True,ast=True)) + ' ' + str(cmds.playbackOptions(q=True,aet=True))

	if os.path.exists(abcFile):
		confirm = cmds.confirmDialog( title='Publish Camera', \
		message='This will replace any previously published camera. Check your parameters : \n\nSHOT NAME :\n%s\n\nFRAME RANGE : \n%s' %(shotCam,frameRange), \
		button=['Continue','Cancel'], \
		defaultButton='Continue', \
		cancelButton='Cancel', \
		dismissString='Cancel' )
		if confirm != 'Continue':
			return

	# backup
	backupPath = scenePath + '/abc/backup'
	backupAbcFile = backupPath + shotCam + '.abc'
	if not os.path.exists(backupPath):
		os.makedirs(backupPath)
	try :
		copyfile(abcFile,backupAbcFile)
	except WindowsError, e :
		cmds.warning('Error : Could not backup file ' + backupAbcFile)
		return

	cmds.select(shotCam,r=True)
	root = cmds.ls(selection=True,l=True)[0]
	print(root)

	# Pause viewport
	cmds.refresh(suspend=True) 

	# Load plugin
	cmds.loadPlugin( 'AbcExport.mll' )

	# Export
	resolvedCmd = '-frameRange %s -step 1 -stripNamespaces -worldSpace -writeVisibility -eulerFilter -dataFormat ogawa -root %s -file %s' \
	 %(frameRange,root,abcFile)
	cmds.AbcExport (j=resolvedCmd)

	# Unpause viewport
	cmds.refresh(suspend=False)

	#Inview message if successful
	if not os.path.exists(abcFile):
		cmds.warning('Camera publish failed, check with Val')
		return

	cmds.inViewMessage(amg='Camera publish successful',pos='midCenter',fade=True)

def contraintCharacterToCar(asset,*args):
	print(asset)
	# propsBrevell
	if asset == 'propsBrevell' or asset == 'characterEthan' or asset == 'propsEthanHelmet' :
		# constraint character to car
		toConstraint = ['characterEthan_rig:C_ROOT_CTRL','characterEthan_rig:L_LEG_bonus_CTRL','characterEthan_rig:R_LEG_bonus_CTRL','characterEthan_rig:L_ARM_CTRL','characterEthan_rig:R_ARM_CTRL']
		for i in toConstraint :
			# check if objects are imported
			if cmds.objExists(i) :
				# delete existing constraints
				constr = i.split(':')[1]+'_parentConstraint1'
				if cmds.objExists(constr):
					cmds.delete(constr)
				# create new constraints
				cmds.parentConstraint('propsBrevell_rig:CTRL_chassis',i,w=1,mo=True)
		# contraint helmet to neck
		if cmds.objExists('propsEthanHelmet_rig:CTRL_mainElmet'):
			cmds.parentConstraint('characterEthan_rig:C_NECK_CTRL','propsEthanHelmet_rig:CTRL_mainElmet',w=1,mo=True)

	# propsWerner
	elif asset == 'propsWerner' or asset == 'characterAlton' or asset == 'propsAltonHelmet':
		# constraint character to car
		toConstraint = ['characterAlton_rig:C_ROOT_CTRL','characterAlton_rig:R_LEG_bonus_CTRL','characterAlton_rig:L_LEG_bonus_CTRL','characterAlton_rig:R_ARM_CTRL','characterAlton_rig:L_ARM_CTRL']
		for i in toConstraint :
			# check if objects are imported
			if cmds.objExists(i) :
				# delete existing constraints
				constr = i.split(':')[1]+'_parentConstraint1'
				if cmds.objExists(constr):
					cmds.delete(constr)
				# create new constraints
				cmds.parentConstraint('propsWerner_rig:CTRL_chassis',i,w=1,mo=True)
		# contraint helmet to neck
		if cmds.objExists('propsAltonHelmet_rig:CTRL_mainElmet'):
			cmds.parentConstraint('characterAlton_rig:C_NECK_CTRL','propsAltonHelmet_rig:CTRL_mainElmet',w=1,mo=True)	

	# End
	else :
		cmds.warning(asset+' isnt supported')
		return

def constraintCharacterToSteeringWheel(asset,*args):
	# propsBrevell
	if asset == 'propsBrevell':
		toConstraint = ['characterEthan_rig:L_ARM_CTRL','characterEthan_rig:R_ARM_CTRL']
		for i in toConstraint :
			# delete previous constraint
			constr = i.split(':')[1]+'_parentConstraint1'
			if cmds.objExists(constr):
				cmds.delete(constr)
			# create new constraint
