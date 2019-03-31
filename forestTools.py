# ****************************************** S K I D     F O R E S T     T O O L S ******************************************

import maya.cmds as cmds
import maya.mel as mel
import os, subprocess

# ****************************************** G L O B A L S ******************************************



# ****************************************** F U N C T I O N S ******************************************

def fireHoudini(focalLength,mtop,mright,mbot,mleft,depth,*args):
	'''This function opens a headless version of houdini and computes
	a point cloud for trees instancing depending on the shot camera position and movements.
	Arguments are camera frustrum margins and should be a float between 0 and 1'''
	
	# User prompt before firing up
	confirmTxt = 'Please check your frame range and margins are right before you continue.'
	confirm = cmds.confirmDialog(title='Compute point cloud',message=confirmTxt,button=['Continue','Cancel'], \
		defaultButton='Continue',cancelButton='Cancel',dismissString='Cancel')
	if confirm != 'Continue':
		return
	# Check current shot
	currentWorkspace = os.path.abspath(cmds.workspace(sn=True,q=True))
	currentShot = str(os.path.split(currentWorkspace)[1])
	# Get Frame range
	fstart = cmds.playbackOptions(ast=True,q=True)
	fend = cmds.playbackOptions(aet=True,q=True)
	# Fire headless Houdini 
	houScript = '//Merlin/3d4/skid/09_dev/toolScripts/publish/houdini/createInstancerPoints.py'
	print(houScript,currentShot,fstart,fend,focalLength,mtop,mright,mbot,mleft,depth)
	# os.system('hython %s %s %s %s %s %s %s %s'%(houScript,currentShot,fstart,fend,mtop,mright,mbot,mleft))
	# os.system('hython //Merlin/3d4/skid/09_dev/toolScripts/publish/houdini/createInstancerPoints.py')
	subprocess.call('hython %s %s %s %s %s %s %s %s %s %s'%(houScript,currentShot,fstart,fend,mtop,mright,mbot,mleft,depth,focalLength))

def loadHoudiniEngine(*args):
	# Load Houdini Engine for Maya and check if version is at least 17
	try :
		cmds.loadPlugin('houdiniEngine')
	except :
		cmds.warning('Could not load Houdini Engine')
		return False
	EngineVersion = mel.eval('houdiniEngine -hv;')
	if not '17.' in EngineVersion :
		cmds.warning('Wrong Houdini Engine version (installed version is '+EngineVersion+'), should be at least version 17')
		return False
	else :
		return True

def loadShotPoints(sector,*args):
	'''This function will load the generated point cloud in Maya via Houdini Engine.
	It will then copy each point and their attribute to a new point cloud to get rid of Houdini Engine.'''

	# Load Houdini Engine
	if loadHoudiniEngine() == False:
		return

	# Check if point bgeo file exists
	# currentWorkspace = os.path.abspath(cmds.workspace(sn=True,q=True))
	# currentShot = str(os.path.split(currentWorkspace)[1])
	# bgeoPath = '//Merlin/3d4/skid/05_shot/%s/geo/fileCache/%s_instancerPts.bgeo.sc'%(currentShot,currentShot)
	bgeoPath = '//Merlin/3d4/skid/04_asset/set/setForest/geo/pointCloud_sector%s.bgeo.sc'%sector

	# Set persp far clip plane
	cmds.setAttr('perspShape.farClipPlane',1000000)

	# Set current time to first frame
	fstart = cmds.playbackOptions(ast=True,q=True)
	cmds.currentTime(fstart)

	# Load the bgeo importer
	toolBgeoToMaya = os.path.abspath('//merlin/3d4/skid/04_asset/hda/toolBgeoToMaya_v2.hdanc')
	cmds.houdiniAsset(la=[toolBgeoToMaya,'Object/toolBgeoToMaya'])
	# Set file path to shot points
	cmds.setAttr('toolBgeoToMaya1.houdiniAssetParm.houdiniAssetParm_file',bgeoPath,type="string")
	# Sync asset
	# cmds.evalDeferred('cmds.houdiniAsset(syn="toolBgeoToMaya1")')
	cmds.houdiniAsset(syn="toolBgeoToMaya1")


	# Duplicate point cloud to get rid of houdini engine
	pointCloud = 'file_bgeoToMaya_0'
	pointCloud_s = pointCloud+'Shape'

	# Get particle count
	nbPart = cmds.particle(pointCloud,q=True,ct=True)

	# Create new particle system with suffix
	tmp = cmds.particle(n=pointCloud+'_dupli')
	dupliPartXf = tmp[0]
	dupliPartShp = tmp[1]

	cmds.setAttr(dupliPartShp+'.isDynamic',False)

	# Create rgbPP attribute on the new system
	cmds.addAttr(dupliPartShp,ln='rgbPP',dt='vectorArray')
	cmds.addAttr(dupliPartShp,ln='rgbPP0',dt='vectorArray')
	# Create radiusPP attribute
	cmds.addAttr(dupliPartShp,ln='radiusPP',dt='doubleArray')
	cmds.addAttr(dupliPartShp,ln='radiusPP0',dt='doubleArray')
	# Create index attribute
	cmds.addAttr(dupliPartShp,ln='index',dt='doubleArray')
	cmds.addAttr(dupliPartShp,ln='index0',dt='doubleArray')
	
	# Fill new particle system with positions
	for i in range(nbPart) :
		wPos = cmds.getParticleAttr('%s.pt[%s]'%(pointCloud_s,i),at='position',array=True)
		cmds.emit(o=dupliPartXf,pos=[wPos[0],wPos[1],wPos[2]])

	# Transfer rgbPP
	for i in range(nbPart) :
		attrValue = cmds.getParticleAttr('%s.pt[%s]'%(pointCloud_s,i),at='rgbPP',array=True)
		cmds.particle(e=True,at='rgbPP',order=i,vectorValue=[attrValue[0],attrValue[1],attrValue[2]])
	
	# Transfer radiusPP
	for i in range(nbPart) :
		attrValue = cmds.getParticleAttr('%s.pt[%s]'%(pointCloud_s,i),at='radiusPP',array=True)
		cmds.particle(e=True,at='radiusPP',order=i,floatValue=attrValue[0])
	
	# Transfer index
	for i in range(nbPart) :
		attrValue = cmds.getParticleAttr('%s.pt[%s]'%(pointCloud_s,i),at='index',array=True)
		cmds.particle(e=True,at='index',order=i,floatValue=attrValue[0])

	# Delete unwanted nodes
	cmds.delete('toolBgeoToMaya1')

	# Rename particle system and group
	newname = 'forest_instancing_pc'
	cmds.rename(tmp[0],newname)
	masterGRP = 'FOREST_INSTANCING_GRP'
	try :
		cmds.select(masterGRP,r=True)
	except ValueError :
		cmds.group(newname,name=masterGRP)
	else :
		cmds.parent(newname,masterGRP)

	# Set nucleus (yes we have to keep it for some reason)
	cmds.setAttr('nucleus1.startFrame',fstart)
	cmds.parent('nucleus1',masterGRP)

def createInstancer(*args):
	'''This function will import every asset needed for instancing
	and create an instancer with index binding'''

	propsPath = '//merlin/3d4/skid/04_asset/props/'

	# The following assets must be in the same order that was specified in Houdini
	toImport = [ \
	# forest
	'propsPine/propsPine_A', #0
	'propsPine/propsPine_B', #1
	'propsPine/propsPine_C', #2
	'propsFir/propsFir_A', #3
	'propsFir/propsFir_B', #4
	# forestGround
	'propsRock/propsRock_A_mossy', #5
	'propsRock/propsRock_B_granite', #6
	'propsRock/propsRock_C_sandstone', #7
	'propsRock/propsRock_D_volcanic', #8
	'propsRock/propsRock_E_volcanic', #9
	'propsRock/propsRock_F_sandstone', #10
	'propsRock/propsRock_G', #11
	'propsBranch/propsBranch_A_branch', #12
	'propsBranch/propsBranch_E_log', #13
	'propsStump/propsStump_A', #14
	'propsStump/propsStump_B', #15
	'propsStump/propsStump_C', #16
	# grassCut
	'propsGrass/propsGrass_A_clean', #17
	'propsGrass/propsGrass_B_clean', #18
	'propsGrass/propsGrass_C_clean', #19
	# grassWild
	'propsGrass/propsGrass_D_long', #20
	'propsGrass/propsGrass_E_long', #21
	'propsGrass/propsGrass_F_long', #22
	'propsGrass/propsGrass_G_long', #23
	'propsGrass/propsGrass_H_coarse', #24
	'propsDandelion/propsDandelion_A', #25
	'propsDandelion/propsDandelion_B', #26
	'propsDandelion/propsDandelion_C', #27
	'propsFern/propsFern_A_small', #28
	'propsFern/propsFern_B_small', #29
	'propsFern/propsFern_C_small', #30
	'propsFern/propsFern_D_big', #31
	'propsFern/propsFern_E_big', #32
	'propsFern/propsFern_F_big', #33
	]

	# Import assets
	for asset in toImport :
		resolvePath = propsPath + asset + '.ma'
		cmds.file(resolvePath,reference=True,type='mayaAscii',ignoreVersion=True)

	toInstance = []
	for i in toImport :
		i = i.split('/')[1]
		i = i.split('.')[0]
		i = i + '_rig:' + i + '_master'
		toInstance.append(i)

	sel = cmds.select(toInstance,r=True)

	# Creating the instancer with pymel seems to be more stable for some reason
	import pymel.core as pm
	instancer = pm.effects.particleInstancer('forest_instancing_pcShape', \
		levelOfDetail='BoundingBox', \
		scale='radiusPP', \
		objectIndex='index', \
		rotation='rgbPP')

	# Rename instancer and group
	instancer = cmds.rename(instancer,'forest_instancing_instancer')
	masterGRP = 'FOREST_INSTANCING_GRP'
	try :
		cmds.select(masterGRP,r=True)
	except ValueError :
		cmds.group(instancer,name=masterGRP)
	else :
		cmds.parent(instancer,masterGRP)

	# Group instanced assets
	instancedGRP = cmds.group(em=True,name='instanced_assets_grp')
	for i in toInstance :
		cmds.parent(i,instancedGRP)
	cmds.parent(instancedGRP,masterGRP)
	# NE PAS DESACTIVER VISIBILITY

def importForest(sector,*args):
	'''This will import a generated RIB containing the instanced forest'''
	
	ribFile = '//Merlin/3d4/skid/04_asset/set/setForest/setForest_sector'+sector+'.rib'

	# 1. Check if exists
	if not os.path.exists(ribFile) :
		cmds.warning('Could not find ' + ribFile)
		return

	importedName = 'setForest_sector'+sector

	if cmds.objExists(importedName) :
		cmds.delete(importedName)
	
	# 2. import
	mel.eval('file -import -type "RIB"  -ignoreVersion -ra true -mergeNamespacesOnClash false  -pr  -importTimeRange "combine" "%s";'%(ribFile))

	# 3. set render stats
	cmds.setAttr(importedName+'Shape.visibleInReflections',1)
	cmds.setAttr(importedName+'Shape.visibleInRefractions',1)