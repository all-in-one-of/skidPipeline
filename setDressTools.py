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

	shotDress = scenePath + '/geo/' + shotName + '_setDress.ma'

	# 1. Check if setdress group exists :
	if not cmds.objExists('SETDRESS_GRP'):
		cmds.warning('SETDRESS_GRP does not exist.')
		return

	# 2. Check if setDress file already exists
	if os.path.exists(shotDress) :
		confirm = cmds.confirmDialog(title='Publish Set Dress', \
			message='You are about to publish the Set Dress for ' + shotName + '. This will erase the currently published set dress. Please note that there is NO BACKUP. Continue ?', \
			button=['Continue','Cancel'], \
			defaultButton='Continue', \
			cancelButton='Cancel', \
			dismissString='Cancel' )
		if confirm != 'Continue':
			return

	# 2. Export
	cmds.select('SETDRESS_GRP',r=True)

	cmds.file(shotDress, \
		type='mayaAscii', \
		exportSelected=True, \
		force=True, \
		preserveReferences=False)

	# 3. inview message
	print('// Result : ' + shotDress)
	cmds.inViewMessage( \
		amg='Set Dress has been publish to <hl>' + shotDress + '</hl>', \
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
		ns=ns)