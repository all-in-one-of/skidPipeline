# ****************************************** S K I D     S E T D R E S S     T O O L S ******************************************

import maya.cmds as cmds
import maya.mel as mel
import os,shutil,datetime
import commonTools

referenceNodes = cmds.ls(type='reference')

# ****************************************** F U N C T I O N S ******************************************

def RNfromSelection():
	'''This will select every master reference node for selected geometries that has a controller'''
	# 1. controllers from selection
	ctrls = []
	for n in cmds.ls(selection=True,referencedNodes=True) :
		if not 'ctrl' in n:
			pass
		else :
			ctrls.append(n)
	# 2. master reference node from ctrl
	rn = []
	for ctrl in ctrls:
		n = cmds.referenceQuery(ctrl,referenceNode=True,p=True)
		rn.append(n)
	return rn

def allRN():
	# Returns all Reference nodes in the scnene
	rn = []
	for n in cmds.ls():
		if not 'RN' in n:
			pass
		else:
			rn.append(n)
	return rn

def unloadSelected():
	for n in RNfromSelection():
		cmds.file(referenceNode=n,unloadReference=True)

# def loadSelected():
# 	for n in RNfromSelection():
# 		cmds.file(referenceNode=n,loadReference=True)

def loadAllReferences():
	sel = cmds.ls(selection=True)
	rn = []
	for i in sel :
		print(i)
		rn.append(cmds.referenceQuery(i,filename=True))
	for i in rn :
		print(i)
		cmds.file(i,force=True,reference=True,loadReferenceDepth='all')

def publishSetDress(*args):
	scenePath = cmds.workspace(sn=True,q=True)
	scenePath = scenePath.replace(os.sep, '/')
	shotName = os.path.split(scenePath)[1]

	maPublish = scenePath + '/geo/' + shotName + '_setDress.ma'

	# 1. Check if setdress group exists :
	if not cmds.objExists('setDress_grp'):
		cmds.warning('setDress_grp does not exist.')
		return

	# 2. Check if setDress file already exists
	if os.path.exists(maPublish) :
		confirm = cmds.confirmDialog(title='Publish Set Dress', \
			message='You are about to publish the Set Dress for ' + shotName + '. This will erase the currently published set dress. Please note that there is NO BACKUP. Continue ?', \
			button=['Continue','Cancel'], \
			defaultButton='Continue', \
			cancelButton='Cancel', \
			dismissString='Cancel' )
		if confirm != 'Continue':
			return

	# 2. Export
	sel = cmds.select('setDress_grp',r=True)

	# a. mayaAscii publish
	cmds.file(maPublish, \
		type='mayaAscii', \
		exportSelected=True, \
		force=True, \
		preserveReferences=False)

	# 4. inview message
	print('// Result : ' + maPublish)
	cmds.inViewMessage( \
		amg='Set Dress publish successful', \
		pos='midCenter', \
		fade=True)

def publishSetDressGPU(*args):
	scenePath = cmds.workspace(sn=True,q=True)
	scenePath = scenePath.replace(os.sep, '/')

	abcPublishPath = scenePath + '/abc'
	abcPublishFile = 'setDressGPU'

	# 1. Check if setdress group exists :
	if not cmds.objExists('setDress_grp'):
		cmds.warning('setDress_grp does not exist.')
		return

	# 2. Export
	sel = cmds.select('setDress_grp',r=True)

	# alembic publish
	cmds.gpuCache('setDress_grp', \
		startTime=1, \
		endTime=1, \
		optimize=True, \
		optimizationThreshold=100, \
		writeMaterials=False, \
		dataFormat='ogawa', \
		useBaseTessellation=True, \
		directory=abcPublishPath, \
		fileName=abcPublishFile)

	# 4. inview message
	print('// Result : ' + abcPublishPath + abcPublishFile)
	cmds.inViewMessage( \
		amg='Set Dress GPU publish successful', \
		pos='midCenter', \
		fade=True)

def importSector(sector,*args):
	'''This will import the specified sector'''
	
	# 1. create namespace
	ns = 'setSector' + sector

	# 2. Check if file exists 
	sector = '//Merlin/3d4/skid/04_asset/set/setSector' + sector + '/setSector' + sector + '.ma'
	if not os.path.exists(sector) :
		cmds.warning('Could not find ' + sector)
		return

	# 3. Check if imported
	importedName = ns + ':' + ns + '_grp'
	if cmds.objExists(importedName) :
		cmds.warning(importedName + ' is already imported.')
		return

	cmds.file(sector, \
		r=True, \
		type='mayaAscii', \
		ignoreVersion=True, \
		gl=True, \
		ns=ns, \
		loadReferenceDepth='all')

def importAssetMa(asset,*args):
	if asset == 'propsGround' :
		assetPath = '//Merlin/3d4/skid/04_asset/set/setGleitenstrasse/%s.ma'%asset
	else :
		assetPath = '//Merlin/3d4/skid/04_asset/props/%s/%s.ma'%(asset,asset)
	
	cmds.file(assetPath, \
		r=True, \
		type='mayaAscii', \
		ignoreVersion=True, \
		gl=True, \
		ns=asset)

def autoUpdateSetDress(*args):
	'''This will update the current shot's set dress using maya standalone'''
	import subprocess,glob

	scenePath = cmds.workspace(sn=True,q=True)
	scenePath = scenePath.replace(os.sep, '/')
	shot = os.path.split(scenePath)[1]

	maPublish = '%s/geo/%s_setDress.ma'%(scenePath,shot)
	sceneFile = glob.glob(scenePath+r'/mayaScenes/setDress/'+shot+r'_*_v*.ma')[-1]

	if not sceneFile :
		cmds.error('Cant find setDress scene file')

	if os.path.exists(maPublish):
		try :
			os.rename(maPublish,maPublish)
		except WindowsError, e :
			cmds.error(maPublish.split("/")[1] +' is already open in another application and cant be replaced.')
			return

	if os.path.exists(maPublish):
		confirm = cmds.confirmDialog( title='Auto update set dress', \
			message='This will replace any previously published setDress for this shot. Check your parameters :\n\nSET DRESS SCENE FILE :\n %s \n\nFILE TO PUBLISH : \n%s' %(sceneFile,maPublish), \
			button=['Continue','Cancel'], \
			defaultButton='Continue', \
			cancelButton='Cancel', \
			dismissString='Cancel' )
		if confirm != 'Continue':
			return

	script = '//Merlin/3d4/skid/09_dev/toolScripts/publish/mayapy/updateSetDress.py'
	subprocess.Popen(['mayapy',script,shot])