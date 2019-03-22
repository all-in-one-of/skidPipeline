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
	cmds.setAttr("hardwareRenderingGlobals.motionBlurEnable",0)
	# cmds.setAttr('hardwareRenderingGlobals.motionBlurSampleCount',16)
	cmds.setAttr('hardwareRenderingGlobals.ssaoEnable',1)
	cmds.setAttr('hardwareRenderingGlobals.ssaoSamples',32)
	cmds.setAttr('hardwareRenderingGlobals.ssaoRadius',64)
	cmds.setAttr('hardwareRenderingGlobals.ssaoFilterRadius',32)

	mel.eval('setObjectDetailsVisibility(0);') # Desactive Object Details
	mel.eval('setCameraNamesVisibility(1);') # Active Camera Name
	mel.eval('setCurrentFrameVisibility(1);') # Active Current Frame
	mel.eval('setFocalLengthVisibility(1);') # Active longueur focale
	# Viewport hide all but geometries
	viewport = cmds.getPanel(withFocus=True)
	cmds.modelEditor(viewport,e=1,allObjects=0)
	cmds.modelEditor(viewport,e=1, \
		pluginObjects=('gpuCacheDisplayFilter',1), \
		polymeshes=1, \
		displayTextures=1)

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

	cmds.setAttr("hardwareRenderingGlobals.motionBlurEnable",0)
	cmds.setAttr('hardwareRenderingGlobals.ssaoEnable',0)
	cmds.setAttr("hardwareRenderingGlobals.multiSampleEnable",0)

	# viewport display all
	cmds.modelEditor(viewport,e=1,allObjects=1)
	# Unpause viewport
	cmds.refresh(suspend=False)

	# Read playblast
	if publish == False :
		os.startfile(playblastPath)

def publishAnimations(*args):
	'''This will publish the current working rig with selected sets in maya 
	standalone and automatically backup any previously published animation'''
	import subprocess

	selectionSets = cmds.ls(selection=True)

	# Check if save has unsaved changes
	if cmds.file(q=True,modified=True) :
		cmds.warning('Save your scene before publishing')
		ret

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

	# Deduce asset
	asset = ns[0].split('_')[0]

	# prepare confirm dialog
	frameRange = str(cmds.playbackOptions(q=True,ast=True)) + '-' + str(cmds.playbackOptions(q=True,aet=True))
	sceneFile = cmds.file(query=True,sceneName=True)

	# confirm dialog
	confirm = cmds.confirmDialog( title='Publish Animation', \
		message='This will replace any previously published animation. Check your parameters : \n\nSCENE FILE :\n %s \n\nASSET : \n%s \n\nSELECTION SETS : \n%s \n\nFRAME RANGE : \n%s' %(sceneFile,asset,selectionSets,frameRange), \
		button=['Continue','Cancel'], defaultButton='Continue', cancelButton='Cancel', dismissString='Cancel' )
	if confirm != 'Continue':
		return

	# fire mayapy
	publishScript = '//Merlin/3d4/skid/09_dev/toolScripts/publish/mayapy/publishAnim.py'
	# resolvedSelectionSets = ''
	# for i in selectionSets :
	# 	resolvedSelectionSets = resolvedSelectionSets + ' ' + i
	# subprocess.call('mayapy "%s" %s %s%s'%(publishScript,sceneFile,asset,resolvedSelectionSets))
	# print resolvedSelectionSets
	subprocess.Popen(['mayapy',publishScript,sceneFile,asset]+selectionSets)



def constraintCar(asset,*args):
	constraints = ['FR','FL','RR','RL']
	attrList = [ \
	asset+'_rig:CTRL_roue_RR_offset_parentConstraint1.Fit_to_ground_RRW0', \
	asset+'_rig:CTRL_roue_RL_offset_parentConstraint1.Fit_to_ground_RLW0', \
	asset+'_rig:CTRL_roue_FL_offset_parentConstraint1.Fit_to_ground_FLW0', \
	asset+'_rig:CTRL_roue_FR_offset_parentConstraint1.Fit_to_ground_FRW0' ]
	sel = cmds.ls(selection=True)

	if len(sel) != 1:
		cmds.warning('More than one object is selected')
		return

	sel = cmds.listRelatives(sel,shapes=True)
	
	for attr in attrList :
		cmds.setAttr(attr,1)

	for const in constraints :
		cmds.select(asset + '_rig:Fit_to_ground_'+const+'_offset',add=True)
		cmds.geometryConstraint(weight=1)
		cmds.select(asset + '_rig:Fit_to_ground_'+const+'_offset',tgl=True)

	cmds.setAttr(sel[0]+'.visibility',0)

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
	cmds.select(asset+'_rig:CTRL',r=True)
	cmds.file('//merlin/3d4/skid/04_asset/character/'+asset+'/data/startPose.atom',  \
		i=True, \
		type='atomImport', \
		ra=True, \
		namespace='poseCar', \
		options=';;targetTime=3;option=scaleReplace;match=hierarchy;;selected=selectedOnly;search=;replace=;prefix=;suffix=;mapFile=;')
	cmds.select(asset+'_rig:CTRL',r=True)